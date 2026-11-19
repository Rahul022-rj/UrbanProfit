

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RENT_FILE = ROOT / "data/raw/urbanprofit_commercial_rent.csv"
MARKET_FILE = ROOT / "data/processed/urbanprofit_market_dataset_enriched.csv"
ROAD_FILE = ROOT / "data/processed/urbanprofit_road_accessibility.csv"

OUTPUT_FILE = ROOT / "data/processed/urbanprofit_market_dataset_final.csv"

# Load datasets
rent = pd.read_csv(RENT_FILE)
market = pd.read_csv(MARKET_FILE)
road = pd.read_csv(ROAD_FILE)

# Calculate median asking rent by locality
rent["rent_per_sqft"] = pd.to_numeric(
    rent["rent_per_sqft"], errors="coerce"
)

rent_summary = rent.groupby("locality").agg(
    commercial_rent_per_sqft=("rent_per_sqft", "median"),
    rent_listing_count=("rent_per_sqft", "count")
).reset_index()

# Merge rent data
final = market.drop(
    columns=["commercial_rent_per_sqft"],
    errors="ignore"
).merge(
    rent_summary,
    on="locality",
    how="left",
    validate="one_to_one"
)

# Merge road accessibility
road_columns = [
    "locality",
    "road_segment_count",
    "total_road_length_km",
    "intersection_count",
    "road_density_km_per_sq_km"
]

final = final.drop(
    columns=[
        "road_segment_count",
        "total_road_length_km",
        "intersection_count",
        "road_density_km_per_sq_km"
    ],
    errors="ignore"
).merge(
    road[road_columns],
    on="locality",
    how="left",
    validate="one_to_one"
)

# Save final dataset
final.to_csv(OUTPUT_FILE, index=False)

print("\nFINAL DATASET CREATED")
print("=" * 45)
print("Shape:", final.shape)
print("Localities:", final["locality"].nunique())

print("\nRent summary:")
print(final[[
    "locality",
    "commercial_rent_per_sqft",
    "rent_listing_count"
]].to_string(index=False))

print("\nMissing values:")
print(final.isnull().sum())

print("\nSaved:", OUTPUT_FILE)
