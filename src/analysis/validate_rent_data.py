
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FILE = ROOT / "data/raw/urbanprofit_commercial_rent.csv"

df = pd.read_csv(FILE)

print("\nURBANPROFIT RENT DATA VALIDATION")
print("=" * 45)

# Check records
print("Total records:", len(df))
print("Total localities:", df["locality"].nunique())

# Convert numeric columns
df["monthly_rent_inr"] = pd.to_numeric(
    df["monthly_rent_inr"], errors="coerce"
)

df["area_sqft"] = pd.to_numeric(
    df["area_sqft"], errors="coerce"
)

df["rent_per_sqft"] = pd.to_numeric(
    df["rent_per_sqft"], errors="coerce"
)

# Validate rent calculations
df["calculated_rent"] = (
    df["monthly_rent_inr"] / df["area_sqft"]
)

df["calculation_valid"] = (
    (df["calculated_rent"] - df["rent_per_sqft"]).abs() < 0.02
)

print("\nMissing values:")
print(df[[
    "locality",
    "monthly_rent_inr",
    "area_sqft",
    "rent_per_sqft",
    "source_url"
]].isnull().sum())

print("\nRent calculation validation:")
print(
    "Valid calculations:",
    df["calculation_valid"].sum()
)
print(
    "Invalid calculations:",
    (~df["calculation_valid"]).sum()
)

print("\nListings per locality:")
print(df.groupby("locality").size())

print("\nLocality-wise rent summary:")

summary = df.groupby("locality").agg(
    listing_count=("rent_per_sqft", "count"),
    minimum_rent=("rent_per_sqft", "min"),
    median_rent=("rent_per_sqft", "median"),
    maximum_rent=("rent_per_sqft", "max")
).round(2)

print(summary)

# Save summary
output = ROOT / "data/processed/urbanprofit_rent_summary.csv"

summary.to_csv(output)

print("\nSummary saved:", output)
