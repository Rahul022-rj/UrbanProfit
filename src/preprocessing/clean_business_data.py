
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

INPUT_FILE = Path("data/raw/bengaluru_businesses_osm_v2.csv")
OUTPUT_FILE = Path("data/processed/bengaluru_businesses_cleaned.csv")

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

print("\n" + "=" * 60)
print("URBANPROFIT - DATA PREPROCESSING")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print("\nOriginal dataset shape:", df.shape)

# --------------------------------------------------
# 3. REMOVE EXACT DUPLICATE ROWS
# --------------------------------------------------

before = len(df)

df = df.drop_duplicates()

print("\nExact duplicate rows removed:", before - len(df))

# --------------------------------------------------
# 4. CHECK OSM IDENTITIES
# --------------------------------------------------

before = len(df)

df = df.drop_duplicates(
    subset=["element", "osmid"],
    keep="first"
)

print("Duplicate OSM identities removed:", before - len(df))

# --------------------------------------------------
# 5. HANDLE BUSINESS NAMES
# --------------------------------------------------

# Preserve missing names rather than deleting records.
# Add a flag to identify records without a mapped name.

df["has_name"] = df["name"].notna().astype(int)

print("\nBusinesses with names:", df["has_name"].sum())
print("Businesses without names:", (df["has_name"] == 0).sum())

# --------------------------------------------------
# 6. STANDARDIZE TEXT COLUMNS
# --------------------------------------------------

text_columns = [
    "element",
    "name",
    "business_category",
    "amenity",
    "shop",
    "leisure",
    "addr:street",
    "addr:suburb",
    "addr:city",
    "locality",
    "source"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

# --------------------------------------------------
# 7. CONVERT NUMERIC COLUMNS
# --------------------------------------------------

df["latitude"] = pd.to_numeric(
    df["latitude"], errors="coerce"
)

df["longitude"] = pd.to_numeric(
    df["longitude"], errors="coerce"
)

df["osmid"] = pd.to_numeric(
    df["osmid"], errors="coerce"
)

# --------------------------------------------------
# 8. CONVERT DATE COLUMN
# --------------------------------------------------

df["collected_at_utc"] = pd.to_datetime(
    df["collected_at_utc"],
    errors="coerce",
    utc=True
)

# --------------------------------------------------
# 9. VALIDATE REQUIRED COLUMNS
# --------------------------------------------------

required_columns = [
    "element",
    "osmid",
    "business_category",
    "latitude",
    "longitude",
    "locality"
]

missing_required = df[required_columns].isnull().sum()

print("\nMissing values in required columns:")
print(missing_required)

# Remove records only if essential fields are missing.

before = len(df)

df = df.dropna(subset=required_columns)

print(
    "\nRecords removed due to missing required values:",
    before - len(df)
)

# --------------------------------------------------
# 10. VALIDATE COORDINATES
# --------------------------------------------------

valid_coordinates = (
    df["latitude"].between(-90, 90)
    & df["longitude"].between(-180, 180)
)

before = len(df)

df = df[valid_coordinates].copy()

print("Records removed due to invalid coordinates:", before - len(df))

# --------------------------------------------------
# 11. REORDER COLUMNS
# --------------------------------------------------

df = df[
    [
        "element",
        "osmid",
        "name",
        "has_name",
        "business_category",
        "amenity",
        "shop",
        "leisure",
        "latitude",
        "longitude",
        "addr:street",
        "addr:suburb",
        "addr:city",
        "locality",
        "source",
        "collected_at_utc"
    ]
]

# --------------------------------------------------
# 12. SAVE PROCESSED DATASET
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 13. FINAL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETED")
print("=" * 60)

print("\nFinal dataset shape:", df.shape)

print("\nCategory distribution:")
print(df["business_category"].value_counts())

print("\nLocality distribution:")
print(df["locality"].value_counts())

print("\nMissing values after preprocessing:")
print(df.isnull().sum())

print("\nSaved processed dataset:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
