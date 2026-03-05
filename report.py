"""
CarbonROI — report.py
======================
Aggregates ROI + environmental results across all cities.
Prints a formatted summary to terminal.
Exports: CSV, Excel (.xlsx)

Usage:
    python report.py
    python report.py --material hdpe
    python report.py --material aluminum --years 20
"""

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from materials import MATERIALS, CITIES, Material, City
from calculator import calc_all_cities, yearly_cashflow
from environmental import calc_environmental_all, total_impact


# ── HELPERS ─────────────────────────────────────────────────────────────────

def fmt_usd(n: float) -> str:
    if abs(n) >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"${n/1_000:.0f}K"
    return f"${n:.0f}"

def fmt_tons(n: float) -> str:
    return f"{n:,.1f}t"


# ── SUMMARY DATAFRAME ────────────────────────────────────────────────────────

def build_summary_df(roi_results, env_results) -> pd.DataFrame:
    """One row per city with all key metrics."""
    rows = []
    env_map = {r.city_name: r for r in env_results}

    for r in roi_results:
        city_label = f"{r.city.name}, {r.city.state}"
        env = env_map.get(city_label)
        rows.append({
            "City":                    r.city.name,
            "State":                   r.city.state,
            "Population":              r.city.population,
            "Benches":                 r.city.bench_count,
            "Climate Zone":            r.city.climate_zone,
            "Climate Multiplier":      r.city.climate_mult,
            "Traditional Material":    r.traditional.material_name,
            "Traditional TCO ($)":     round(r.traditional.total),
            "Carbon Fiber TCO ($)":    round(r.carbon_fiber.total),
            "Net Savings ($)":         round(r.net_savings),
            "Savings (%)":             round(r.savings_pct, 1),
            "Break-Even Year":         r.break_even_year,
            "Trad Replacements":       r.traditional.replacements,
            "CF Replacements":         r.carbon_fiber.replacements,
            "CO2 Avoided (tons)":      env.co2_avoided_tons if env else None,
            "Waste Prevented (tons)":  env.waste_prevented_tons if env else None,
            "Cars Off Road":           env.cars_off_road if env else None,
            "Trees Equivalent":        env.trees_equivalent if env else None,
            "Analysis Date":           date.today().isoformat(),
        })

    df = pd.DataFrame(rows)
    return df.sort_values("Net Savings ($)", ascending=False).reset_index(drop=True)


def build_yearly_df(cities: list[City], trad_mat: Material,
                    cf_mat: Material, years: int) -> pd.DataFrame:
    """Year-by-year cashflow for all cities stacked."""
    frames = []
    for city in cities:
        df = yearly_cashflow(city, trad_mat, cf_mat, years)
        df.insert(0, "state", city.state)
        df.insert(0, "city",  city.name)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ── TERMINAL PRINT ───────────────────────────────────────────────────────────

def print_report(summary_df: pd.DataFrame, totals: dict,
                 trad_name: str, years: int) -> None:

    W = 80
    print("\n" + "═" * W)
    print(f"  🏙️  CarbonROI — Smart City Infrastructure Analysis")
    print(f"  Carbon Fiber vs {trad_name} | {years}-year horizon | {date.today()}")
    print("═" * W)

    # Per-city table
    print(f"\n  {'#':<3} {'City':<22} {'Savings':>10} {'Sav%':>6} "
          f"{'Break-Even':>11} {'CO₂ Avoided':>12}")
    print("  " + "─" * (W - 2))

    for i, row in summary_df.iterrows():
        star = "★ " if i == 0 else f"{i+1}. "
        be   = f"Year {int(row['Break-Even Year'])}" if row['Break-Even Year'] else "  N/A"
        print(f"  {star:<3}"
              f"{row['City']+', '+row['State']:<22}"
              f"{fmt_usd(row['Net Savings ($)']):>10}"
              f"{row['Savings (%)']:>5.1f}%"
              f"{be:>12}"
              f"{fmt_tons(row['CO2 Avoided (tons)']):>12}")

    # Totals
    print("  " + "─" * (W - 2))
    total_savings = summary_df["Net Savings ($)"].sum()
    print(f"  {'TOTAL':<25}"
          f"{fmt_usd(total_savings):>10}"
          f"{'':>18}"
          f"{fmt_tons(totals['total_co2_avoided_tons']):>12}")

    # Environmental summary
    print(f"\n  🌱 Environmental Impact (combined, {years} years)")
    print("  " + "─" * (W - 2))
    print(f"  CO₂ avoided:              {totals['total_co2_avoided_tons']:,.1f} metric tons")
    print(f"  Waste prevented:          {totals['total_waste_prevented_tons']:,.1f} metric tons")
    print(f"  Cars off road (1yr equiv):{totals['total_cars_off_road']:>10,}")
    print(f"  Trees equivalent:         {totals['total_trees_equivalent']:>10,}")
    print(f"  Benches not manufactured: {totals['total_benches_not_replaced']:>10,}")

    print("\n" + "═" * W + "\n")


# ── EXPORT ───────────────────────────────────────────────────────────────────

def export(summary_df: pd.DataFrame, yearly_df: pd.DataFrame,
           totals: dict, out_dir: Path) -> None:

    out_dir.mkdir(parents=True, exist_ok=True)

    # CSV — summary
    csv_path = out_dir / "CarbonROI_Summary.csv"
    summary_df.to_csv(csv_path, index=False)
    print(f"  ✅ {csv_path}")

    # CSV — yearly cashflow
    yearly_path = out_dir / "CarbonROI_Yearly.csv"
    yearly_df.to_csv(yearly_path, index=False)
    print(f"  ✅ {yearly_path}")

    # Excel — multi-sheet
    xlsx_path = out_dir / "CarbonROI_Report.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        yearly_df.to_excel(writer, sheet_name="Yearly Cashflow", index=False)

        # Totals sheet
        totals_df = pd.DataFrame([totals])
        totals_df.to_excel(writer, sheet_name="Totals", index=False)

        # Auto-width columns
        for sheet in writer.sheets.values():
            for col in sheet.columns:
                max_len = max(len(str(c.value or "")) for c in col) + 2
                sheet.column_dimensions[col[0].column_letter].width = min(max_len, 30)

    print(f"  ✅ {xlsx_path}")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CarbonROI report generator")
    parser.add_argument("--material", default="steel",
                        choices=["steel", "hdpe", "aluminum"],
                        help="Traditional material to compare against CF")
    parser.add_argument("--years", type=int, default=30,
                        help="Analysis horizon in years")
    parser.add_argument("--cf-price", type=float, default=1200,
                        help="Carbon fiber bench unit price (USD)")
    parser.add_argument("--out", default="output",
                        help="Output directory for exported files")
    args = parser.parse_args()

    # Override CF price if specified
    cf_mat = MATERIALS["carbon_fiber"]
    if args.cf_price != 1200:
        from dataclasses import replace
        cf_mat = replace(cf_mat, unit_cost=args.cf_price)

    trad_mat = MATERIALS[args.material]

    print(f"\n  Running analysis: CF ${args.cf_price:,} vs {trad_mat.name} | {args.years}yr...")

    # Calculate
    roi_results = calc_all_cities(CITIES, trad_mat, cf_mat, args.years)
    env_results = calc_environmental_all(CITIES, trad_mat, cf_mat, args.years)
    totals      = total_impact(env_results)

    # Build dataframes
    summary_df = build_summary_df(roi_results, env_results)
    yearly_df  = build_yearly_df(CITIES, trad_mat, cf_mat, args.years)

    # Print
    print_report(summary_df, totals, trad_mat.name, args.years)

    # Export
    print("  📥 Exporting files...")
    export(summary_df, yearly_df, totals, Path(args.out))
    print()


if __name__ == "__main__":
    main()
