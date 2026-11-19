
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. LOAD PROCESSED DATA
# --------------------------------------------------

INPUT_FILE = Path(
    "data/processed/bengaluru_businesses_cleaned.csv"
)

OUTPUT_FILE = Path(
    "data/processed/bengaluru_businesses_features.csv"
)

df = pd.read_csv(INPUT_FILE)

print("\nURBANPROFIT - FEATURE ENGINEERING")
print("=" * 60)

# --------------------------------------------------
# 2. TOTAL BUSINESSES PER LOCALITY
# --------------------------------------------------

locality_totals = (
    df.groupby("locality")
    .size()
    .rename("total_locality_businesses")
)

df = df.merge(
    locality_totals,
    on="locality",
    how="left"
)

# --------------------------------------------------
# 3. BUSINESS COUNT PER LOCALITY AND CATEGORY
# --------------------------------------------------

category_counts = (
    df.groupby(["locality", "business_category"])
    .size()
    .rename("business_count")
    .reset_index()
)

df = df.merge(
    category_counts,
    on=["locality", "business_category"],
    how="left"
)

# --------------------------------------------------
# 4. CATEGORY SHARE
# --------------------------------------------------

df["category_share"] = (
    df["business_count"]
    / df["total_locality_businesses"]
) * 100

# --------------------------------------------------
# 5. GEOGRAPHICAL GRID FEATURES
# --------------------------------------------------

df["latitude_band"] = df["latitude"].round(3)
df["longitude_band"] = df["longitude"].round(3)

# --------------------------------------------------
# 6. SAVE FEATURE DATASET
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 7. DISPLAY RESULTS
# --------------------------------------------------

print("\nNew features created:")
print([
    "total_locality_businesses",
    "business_count",
    "category_share",
    "latitude_band",
    "longitude_band"
])

print("\nLocality and category summary:")

summary = (
    df.groupby(["locality", "business_category"])
    .agg(
        business_count=("osmid", "count"),
        category_share=("category_share", "first")
    )
    .reset_index()
)

print(summary.to_string(index=False))

print("\nFinal dataset shape:", df.shape)

print("\nSaved:", OUTPUT_FILE)

print("\nFEATURE ENGINEERING COMPLETED")
print("=" * 60)
