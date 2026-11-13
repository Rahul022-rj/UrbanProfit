
import os
import pandas as pd

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

MARKET_FILE = "data/raw/urbanprofit_market_indicators.csv"

POPULATION_FILE = (
    "data/processed/urbanprofit_population_estimates.csv"
)

OUTPUT_FILE = (
    "data/processed/urbanprofit_market_dataset_enriched.csv"
)


# --------------------------------------------------
# 2. LOAD DATASETS
# --------------------------------------------------

market = pd.read_csv(MARKET_FILE)
population = pd.read_csv(POPULATION_FILE)

print("Market dataset:", market.shape)
print("Population dataset:", population.shape)


# --------------------------------------------------
# 3. VALIDATE LOCALITY KEYS
# --------------------------------------------------

for name, df in [
    ("Market", market),
    ("Population", population)
]:
    if "locality" not in df.columns:
        raise ValueError(
            f"{name} dataset has no locality column."
        )

    df["locality"] = df["locality"].astype(str).str.strip()

    if df["locality"].duplicated().any():
        raise ValueError(
            f"Duplicate locality found in {name} dataset."
        )


# --------------------------------------------------
# 4. SELECT POPULATION FEATURES
# --------------------------------------------------

population_columns = [
    "locality",
    "population",
    "area_sq_km",
    "population_density",
    "population_year",
    "population_source",
    "source_doi",
    "method"
]

missing = [
    col for col in population_columns
    if col not in population.columns
]

if missing:
    raise ValueError(
        f"Missing population columns: {missing}"
    )

population = population[population_columns]


# --------------------------------------------------
# 5. REMOVE EMPTY POPULATION COLUMNS FROM MARKET DATA
# --------------------------------------------------

population_fields = [
    "population",
    "area_sq_km",
    "population_density",
    "population_year",
    "population_source",
    "source_doi",
    "method"
]

# Remove existing placeholder columns.
# The actual population values will come from WorldPop.
market = market.drop(
    columns=population_fields,
    errors="ignore"
)


# --------------------------------------------------
# 6. MERGE DATASETS
# --------------------------------------------------

merged = market.merge(
    population,
    on="locality",
    how="left",
    validate="one_to_one",
    indicator=True
)

print("\nMerge status:")
print(merged["_merge"].value_counts())

unmatched = merged[
    merged["_merge"] != "both"
]["locality"].tolist()

if unmatched:
    raise ValueError(
        f"Population data missing for: {unmatched}"
    )

merged = merged.drop(columns=["_merge"])


# --------------------------------------------------
# 7. SAVE ENRICHED DATASET
# --------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

merged.to_csv(OUTPUT_FILE, index=False)

print("\nMERGE COMPLETED")
print("=" * 50)

print("Total localities:", len(merged))
print("Total columns:", len(merged.columns))

print("\nPopulation summary:")
print(
    merged[
        [
            "locality",
            "population",
            "population_density"
        ]
    ].to_string(index=False)
)

print("\nSaved:", OUTPUT_FILE)
