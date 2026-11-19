
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

INPUT_FILE = Path(
    "data/processed/bengaluru_businesses_features.csv"
)

OUTPUT_FILE = Path(
    "data/raw/urbanprofit_market_indicators.csv"
)

# --------------------------------------------------
# 2. LOAD EXISTING BUSINESS DATA
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("\nURBANPROFIT - MARKET DATASET CREATION")
print("=" * 60)

# --------------------------------------------------
# 3. GET LOCALITIES
# --------------------------------------------------

localities = sorted(df["locality"].dropna().unique())

# --------------------------------------------------
# 4. CALCULATE COMPETITOR COUNTS
# --------------------------------------------------

competition = pd.crosstab(
    df["locality"],
    df["business_category"]
)

competition = competition.reindex(
    localities,
    fill_value=0
)

competition.columns = [
    "competitors_" + str(col)
    .lower()
    .replace(" / ", "_")
    .replace(" ", "_")
    for col in competition.columns
]

competition = competition.reset_index()

# --------------------------------------------------
# 5. CALCULATE TOTAL MAPPED BUSINESSES
# --------------------------------------------------

total_businesses = (
    df.groupby("locality")
    .size()
    .rename("total_mapped_businesses")
    .reset_index()
)

# --------------------------------------------------
# 6. CREATE MARKET INDICATOR TEMPLATE
# --------------------------------------------------

market_data = competition.merge(
    total_businesses,
    on="locality",
    how="left"
)

# Demographic and economic indicators.
# These will be populated from verified sources later.

market_data["population"] = pd.NA
market_data["area_sq_km"] = pd.NA
market_data["population_density"] = pd.NA
market_data["commercial_rent_per_sqft"] = pd.NA
market_data["metro_distance_km"] = pd.NA
market_data["road_accessibility_score"] = pd.NA

# Data provenance fields
market_data["population_source"] = pd.NA
market_data["population_year"] = pd.NA
market_data["rent_source"] = pd.NA
market_data["rent_reference_date"] = pd.NA
market_data["accessibility_source"] = pd.NA
market_data["notes"] = pd.NA

# --------------------------------------------------
# 7. SAVE DATASET
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

market_data.to_csv(
    OUTPUT_FILE,
    index=False
)

# --------------------------------------------------
# 8. DISPLAY SUMMARY
# --------------------------------------------------

print("\nLocalities:", len(market_data))
print("Total mapped businesses:", df.shape[0])

print("\nMarket dataset:")
print(market_data.to_string(index=False))

print("\nDataset shape:", market_data.shape)
print("\nSaved file:", OUTPUT_FILE)

print("\nMARKET DATASET CREATED SUCCESSFULLY")
print("=" * 60)
