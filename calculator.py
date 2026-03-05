"""
CarbonROI — calculator.py
=========================
TCO (Total Cost of Ownership) and ROI calculations.
Uses climate-adjusted lifespans to model real-world degradation.
"""

import math
from dataclasses import dataclass
from typing import Optional
import pandas as pd

from materials import Material, City


# ── TCO RESULT ─────────────────────────────────────────────────────────────

@dataclass
class TCOResult:
    material_name: str
    city_name: str
    quantity: int
    years: int
    lifespan_adjusted: int      # years, after climate multiplier
    replacements: int           # how many times replaced over analysis period
    capex: float                # total capital expenditure
    opex: float                 # total maintenance expenditure
    total: float                # capex + opex

    @property
    def cost_per_bench_per_year(self) -> float:
        return self.total / self.quantity / self.years


@dataclass
class ROIResult:
    city: City
    traditional: TCOResult
    carbon_fiber: TCOResult
    net_savings: float
    savings_pct: float
    break_even_year: Optional[int]


# ── CORE FUNCTIONS ──────────────────────────────────────────────────────────

def calc_tco(mat: Material, qty: int, years: int, climate_mult: float) -> TCOResult:
    """
    Calculate Total Cost of Ownership for a material.

    Formula:
        lifespan_adj = floor(lifespan_base × climate_mult)
        replacements = floor(years / lifespan_adj)
        capex = (unit_cost + install) × (replacements + 1) × qty
        opex  = maintenance_yr × years × qty
        total = capex + opex
    """
    lifespan_adj = max(1, math.floor(mat.lifespan_yr * climate_mult))
    replacements = math.floor(years / lifespan_adj)
    capex = (mat.unit_cost + mat.install_cost) * (replacements + 1) * qty
    opex  = mat.maintenance_yr * years * qty

    return TCOResult(
        material_name=mat.name,
        city_name="",
        quantity=qty,
        years=years,
        lifespan_adjusted=lifespan_adj,
        replacements=replacements,
        capex=capex,
        opex=opex,
        total=capex + opex,
    )


def find_break_even(trad: Material, cf: Material, qty: int,
                    climate_mult: float, max_years: int = 50) -> Optional[int]:
    """Find the first year when CF cumulative cost drops below traditional."""
    for y in range(1, max_years + 1):
        t = calc_tco(trad, qty, y, climate_mult)
        c = calc_tco(cf,   qty, y, climate_mult)
        if c.total < t.total:
            return y
    return None


def calc_roi(city: City, trad_mat: Material, cf_mat: Material,
             years: int = 30) -> ROIResult:
    """Full ROI analysis for one city."""
    qty  = city.bench_count
    mult = city.climate_mult

    trad_tco = calc_tco(trad_mat, qty, years, mult)
    cf_tco   = calc_tco(cf_mat,   qty, years, mult)

    trad_tco.city_name = city.name
    cf_tco.city_name   = city.name

    savings     = trad_tco.total - cf_tco.total
    savings_pct = savings / trad_tco.total * 100 if trad_tco.total > 0 else 0
    break_even  = find_break_even(trad_mat, cf_mat, qty, mult)

    return ROIResult(
        city=city,
        traditional=trad_tco,
        carbon_fiber=cf_tco,
        net_savings=savings,
        savings_pct=savings_pct,
        break_even_year=break_even,
    )


def calc_all_cities(cities: list[City], trad_mat: Material,
                    cf_mat: Material, years: int = 30) -> list[ROIResult]:
    """Run ROI analysis for all cities."""
    return [calc_roi(city, trad_mat, cf_mat, years) for city in cities]


def yearly_cashflow(city: City, trad_mat: Material, cf_mat: Material,
                    years: int = 30) -> pd.DataFrame:
    """Year-by-year cumulative cost comparison for one city."""
    rows = []
    qty  = city.bench_count
    mult = city.climate_mult

    for y in range(1, years + 1):
        t = calc_tco(trad_mat, qty, y, mult)
        c = calc_tco(cf_mat,   qty, y, mult)
        rows.append({
            "year":             y,
            "traditional_tco":  round(t.total),
            "cf_tco":           round(c.total),
            "cumulative_savings": round(t.total - c.total),
        })

    return pd.DataFrame(rows)


# ── QUICK TEST ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from materials import MATERIALS, CITIES

    trad = MATERIALS["steel"]
    cf   = MATERIALS["carbon_fiber"]

    print(f"TCO Test — New York, 30yr, Steel vs Carbon Fiber")
    print("=" * 55)

    nyc  = next(c for c in CITIES if c.name == "New York")
    result = calc_roi(nyc, trad, cf, years=30)

    print(f"  Benches:          {result.city.bench_count:,}")
    print(f"  Steel TCO:        ${result.traditional.total:>15,.0f}")
    print(f"  Carbon Fiber TCO: ${result.carbon_fiber.total:>15,.0f}")
    print(f"  Net savings:      ${result.net_savings:>15,.0f}")
    print(f"  Savings:          {result.savings_pct:.1f}%")
    print(f"  Break-even:       Year {result.break_even_year}")

    print("\nYear-by-year (first 10 years):")
    df = yearly_cashflow(nyc, trad, cf)
    print(df.head(10).to_string(index=False))
