
import pandas as pd

file_path = "data/raw/bengaluru_businesses_osm_v2.csv"

df = pd.read_csv(file_path)

print("\nURBANPROFIT - OSM DATASET VALIDATION")
print("------------------------------------")

print("Total records:", len(df))
print("Total columns:", len(df.columns))

print("\nBusiness categories:")
print(df["business_category"].value_counts())

print("\nLocalities:")
print(df["locality"].value_counts())

print("\nMissing OSM IDs:", df["osmid"].isna().sum())
print("Missing locality:", df["locality"].isna().sum())
print("Duplicate OSM IDs:", df.duplicated(
    subset=["element", "osmid"]
).sum())

print("\nFirst 10 records:")
print(df.head(10).to_string(index=False))
