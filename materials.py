"""
CarbonROI — materials.py
========================
Dataclasses for materials and cities.
All prices verified from commercial sources (Grainger, ParkWarehouse) — Feb 2026.
"""

from dataclasses import dataclass


@dataclass
class Material:
    """Urban furniture material with cost and lifespan data."""
    key: str
    name: str
    unit_cost: float      # USD, municipal-grade bench
    install_cost: float   # USD, per unit
    lifespan_yr: int      # years, base (temperate climate)
    maintenance_yr: float # USD per unit per year
    co2_kg: float         # kg CO₂ per unit manufactured
    color: str            # hex for charts


@dataclass
class City:
    """US city with infrastructure and climate data."""
    name: str
    state: str
    population: int
    climate_zone: str
    climate_mult: float   # lifespan multiplier (NOAA-based degradation factor)
    benches_per_1k: int   # estimated benches per 1,000 residents

    @property
    def bench_count(self) -> int:
        return round(self.population * self.benches_per_1k / 1000)


# ── MATERIALS ──────────────────────────────────────────────────────────────
# Prices: Grainger.com + ParkWarehouse.com (verified Feb 2026)

MATERIALS = {
    "steel": Material(
        key="steel",
        name="Powder Coated Steel",
        unit_cost=1258,
        install_cost=150,
        lifespan_yr=10,
        maintenance_yr=80,
        co2_kg=125,
        color="#64748b",
    ),
    "hdpe": Material(
        key="hdpe",
        name="Recycled Plastic (HDPE)",
        unit_cost=992,
        install_cost=100,
        lifespan_yr=20,
        maintenance_yr=20,
        co2_kg=45,
        color="#0ea5e9",
    ),
    "aluminum": Material(
        key="aluminum",
        name="Aluminum",
        unit_cost=730,
        install_cost=100,
        lifespan_yr=20,
        maintenance_yr=25,
        co2_kg=85,
        color="#94a3b8",
    ),
    "carbon_fiber": Material(
        key="carbon_fiber",
        name="Carbon Fiber (CFRP)",
        unit_cost=1200,
        install_cost=100,
        lifespan_yr=30,
        maintenance_yr=10,
        co2_kg=30,
        color="#10b981",
    ),
}


# ── CITIES ─────────────────────────────────────────────────────────────────
# Climate multipliers: fraction of base lifespan retained under local conditions.
# 1.0 = temperate ideal, 0.70 = harsh coastal/continental (fastest degradation).

CITIES = [
    City("Miami",           "FL", 442_241,   "Subtropical/Humid",     0.72, 6),
    City("Fort Lauderdale", "FL", 182_437,   "Subtropical/Coastal",   0.70, 6),
    City("New York",        "NY", 8_336_817, "Humid Continental",     0.75, 4),
    City("Los Angeles",     "CA", 3_979_576, "Mediterranean/Arid",    0.95, 4),
    City("Chicago",         "IL", 2_696_555, "Continental/Harsh",     0.70, 4),
    City("Washington",      "DC", 689_545,   "Humid Subtropical",     0.80, 5),
    City("Houston",         "TX", 2_304_580, "Humid Subtropical",     0.75, 4),
    City("Phoenix",         "AZ", 1_608_139, "Desert/Hot",            0.90, 3),
    City("Seattle",         "WA", 749_256,   "Temperate/Wet",         0.80, 5),
    City("San Francisco",   "CA", 873_965,   "Mild/Coastal",          0.85, 5),
]


if __name__ == "__main__":
    print("── Materials ──────────────────────────────────")
    for m in MATERIALS.values():
        print(f"  {m.name:30s} ${m.unit_cost:,} | {m.lifespan_yr}yr | ${m.maintenance_yr}/yr maint")

    print("\n── Cities ─────────────────────────────────────")
    for c in CITIES:
        print(f"  {c.name+', '+c.state:22s} pop {c.population:>9,} | {c.bench_count:>5,} benches | mult {c.climate_mult}")
