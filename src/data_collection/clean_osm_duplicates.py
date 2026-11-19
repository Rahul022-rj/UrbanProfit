
import pandas as pd

INPUT_FILE = "data/raw/bengaluru_businesses_osm_v2.csv"
OUTPUT_FILE = "data/raw/bengaluru_businesses_osm_v2.csv"

df = pd.read_csv(INPUT_FILE)

print("Records before cleaning:", len(df))

# Normalize identifiers.
df["osmid"] = df["osmid"].astype("string").str.strip()
df["element"] = df["element"].astype("string").str.strip()

# Identify records with valid OSM IDs.
valid_ids = (
    df["osmid"].notna()
    & df["osmid"].ne("")
    & df["osmid"].ne("nan")
)

identified = df[valid_ids].drop_duplicates(
    subset=["element", "osmid"],
    keep="first"
)

unidentified = df[~valid_ids]

cleaned = pd.concat(
    [identified, unidentified],
    ignore_index=True
)

cleaned.to_csv(OUTPUT_FILE, index=False)

print("Records after cleaning:", len(cleaned))
print("Duplicates removed:", len(df) - len(cleaned))

print("\nLocality distribution:")
print(cleaned["locality"].value_counts())

print("\nCategory distribution:")
print(cleaned["business_category"].value_counts())

print("\nCleaning completed successfully.")
