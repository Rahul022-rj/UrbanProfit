
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FILE = ROOT / "data/raw/urbanprofit_commercial_rent.csv"

df = pd.read_csv(FILE, dtype={"listing_id": "string"})

# Treat blank IDs as missing
df["listing_id"] = df["listing_id"].str.strip()
df["listing_id"] = df["listing_id"].replace("", pd.NA)

print("\nMISSING LISTING IDs")
print("=" * 50)
print(df[df["listing_id"].isna()][
    ["locality", "monthly_rent_inr", "area_sqft"]
].to_string(index=False))

print("\nDUPLICATE LISTING IDs")
print("=" * 50)

duplicates = df[
    df["listing_id"].notna()
    & df["listing_id"].duplicated(keep=False)
].sort_values("listing_id")

if duplicates.empty:
    print("No duplicate IDs found.")
else:
    print(duplicates[[
        "locality",
        "listing_id",
        "monthly_rent_inr",
        "area_sqft",
        "source_url"
    ]].to_string(index=False))

print("\nSUMMARY")
print("Total rows:", len(df))
print("Missing IDs:", df["listing_id"].isna().sum())
print("Duplicate ID rows:", len(duplicates))
print("Unique non-missing IDs:", df["listing_id"].nunique())
