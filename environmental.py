"""
CarbonROI — environmental.py
=============================
Environmental impact calculations:
- CO₂ emissions avoided
- Waste (material) prevented
- Human-scale equivalents for reports
"""

from dataclasses import dataclass
from materials import Material, City
from calculator import calc_tco


# ── CONSTANTS ───────────────────────────────────────────────────────────────

BENCH_WEIGHT_KG       = 68      # avg weight of a steel park bench (kg)
STEEL_CONTENT_PCT     = 0.30    # fraction of bench that is steel by weight
CO2_PER_TON_STEEL     = 1.85    # tCO₂ per ton of steel produced (World Steel Assoc.)
CO2_PER_CAR_YEAR      = 4.6     # tCO₂ per average US car per year (EPA)
KWH_PER_HOME_YEAR     = 10_500  # kWh consumed by avg US household per year (EIA)
CO2_PER_KWH           = 0.386   # tCO₂ per MWh US grid average (EPA 2023)
TREES_PER_TON_CO2     = 45      # trees needed to absorb 1 tCO₂ over 10 years


# ── RESULT DATACLASS ────────────────────────────────────────────────────────

@dataclass
class EnvironmentalResult:
    city_name: str
    benches_not_replaced: int    # fewer replacement cycles vs traditional
    waste_prevented_kg: float    # kg of material not manufactured/landfilled
    waste_prevented_tons: float  # same in metric tons
    co2_avoided_tons: float      # metric tons CO₂ not emitted
    # equivalents
    cars_off_road: int           # cars removed from road for 1 year
    homes_powered: int           # homes powered for 1 year (via energy savings proxy)
    trees_equivalent: int        # trees needed to absorb same CO₂


# ── CORE FUNCTION ───────────────────────────────────────────────────────────

def calc_environmental(city: City, trad_mat: Material, cf_mat: Material,
                       years: int = 30) -> EnvironmentalResult:
    """
    Calculate environmental savings from switching to carbon fiber.

    Logic:
        - Fewer replacements = less manufacturing = less CO₂ + less waste
        - Waste = (replacements_saved × qty × bench_weight_kg)
        - CO₂   = waste_steel_tons × CO₂_per_ton_steel
    """
    qty  = city.bench_count
    mult = city.climate_mult

    trad_tco = calc_tco(trad_mat, qty, years, mult)
    cf_tco   = calc_tco(cf_mat,   qty, years, mult)

    replacements_saved   = max(0, trad_tco.replacements - cf_tco.replacements)
    waste_prevented_kg   = replacements_saved * qty * BENCH_WEIGHT_KG
    waste_prevented_tons = waste_prevented_kg / 1000

    steel_tons_saved = waste_prevented_kg * STEEL_CONTENT_PCT / 1000
    co2_avoided      = steel_tons_saved * CO2_PER_TON_STEEL

    return EnvironmentalResult(
        city_name=f"{city.name}, {city.state}",
        benches_not_replaced=replacements_saved * qty,
        waste_prevented_kg=round(waste_prevented_kg),
        waste_prevented_tons=round(waste_prevented_tons, 1),
        co2_avoided_tons=round(co2_avoided, 1),
        cars_off_road=round(co2_avoided / CO2_PER_CAR_YEAR),
        homes_powered=round(co2_avoided * 1000 / (KWH_PER_HOME_YEAR * CO2_PER_KWH)),
        trees_equivalent=round(co2_avoided * TREES_PER_TON_CO2),
    )


def calc_environmental_all(cities: list[City], trad_mat: Material,
                            cf_mat: Material, years: int = 30) -> list[EnvironmentalResult]:
    """Run environmental analysis for all cities."""
    return [calc_environmental(city, trad_mat, cf_mat, years) for city in cities]


def total_impact(results: list[EnvironmentalResult]) -> dict:
    """Aggregate environmental totals across all cities."""
    return {
        "total_co2_avoided_tons":    round(sum(r.co2_avoided_tons for r in results), 1),
        "total_waste_prevented_tons": round(sum(r.waste_prevented_tons for r in results), 1),
        "total_cars_off_road":        sum(r.cars_off_road for r in results),
        "total_homes_powered":        sum(r.homes_powered for r in results),
        "total_trees_equivalent":     sum(r.trees_equivalent for r in results),
        "total_benches_not_replaced": sum(r.benches_not_replaced for r in results),
    }


# ── QUICK TEST ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from materials import MATERIALS, CITIES

    trad = MATERIALS["steel"]
    cf   = MATERIALS["carbon_fiber"]

    print("🌱 Environmental Impact — All Cities | 30-year horizon")
    print("=" * 65)
    print(f"  {'City':<22} {'CO₂ Avoided':>12} {'Waste Prev.':>12} {'Cars':>8} {'Trees':>8}")
    print("  " + "-" * 63)

    results = calc_environmental_all(CITIES, trad, cf)
    for r in sorted(results, key=lambda x: -x.co2_avoided_tons):
        print(f"  {r.city_name:<22} {r.co2_avoided_tons:>10.1f}t "
              f"{r.waste_prevented_tons:>10.1f}t "
              f"{r.cars_off_road:>8,} "
              f"{r.trees_equivalent:>8,}")

    totals = total_impact(results)
    print("  " + "-" * 63)
    print(f"  {'TOTAL':<22} {totals['total_co2_avoided_tons']:>10.1f}t "
          f"{totals['total_waste_prevented_tons']:>10.1f}t "
          f"{totals['total_cars_off_road']:>8,} "
          f"{totals['total_trees_equivalent']:>8,}")

    print(f"\n  🏠 Homes powered equivalent: {totals['total_homes_powered']:,}")
    print(f"  🔄 Benches not manufactured: {totals['total_benches_not_replaced']:,}")
