
import os
import pandas as pd
import numpy as np

# ------------------------------------------------
# 1. FILE PATHS
# ------------------------------------------------

INPUT_FILE = (
    "data/synthetic/urbanprofit_market_data_synthetic.csv"
)

OUTPUT_DIR = "data/processed"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "urbanprofit_cleaned.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------
# 2. LOAD DATASET
# ------------------------------------------------

print("\nLoading synthetic dataset...")

df = pd.read_csv(INPUT_FILE)

print("Original dataset shape:", df.shape)

# ------------------------------------------------
# 3. REMOVE DUPLICATE RECORDS
# ------------------------------------------------

print("\nChecking duplicate records...")

duplicates = df.duplicated().sum()

print("Duplicate records:", duplicates)

df = df.drop_duplicates()

# ------------------------------------------------
# 4. HANDLE MISSING VALUES
# ------------------------------------------------

print("\nChecking missing values...")

print(df.isnull().sum())

numeric_columns = df.select_dtypes(
    include=["number"]
).columns

categorical_columns = df.select_dtypes(
    include=["object"]
).columns

for column in numeric_columns:
    df[column] = df[column].fillna(
        df[column].median()
    )

for column in categorical_columns:
    if column == "data_source":
        continue

    if df[column].isnull().any():
        df[column] = df[column].fillna(
            df[column].mode().iloc[0]
        )

# ------------------------------------------------
# 5. CHECK INVALID VALUES
# ------------------------------------------------

print("\nChecking invalid values...")

score_columns = [
    "transport_access_score",
    "income_index",
    "footfall_index",
    "market_potential_score"
]

for column in score_columns:
    df[column] = df[column].clip(0, 100)

df["population_density"] = df[
    "population_density"
].clip(lower=0)

df["competitor_count"] = df[
    "competitor_count"
].clip(lower=0)

df["existing_business_count"] = df[
    "existing_business_count"
].clip(lower=0)

df["avg_monthly_rent"] = df[
    "avg_monthly_rent"
].clip(lower=0)

df["distance_main_road_km"] = df[
    "distance_main_road_km"
].clip(lower=0)

# ------------------------------------------------
# 6. VALIDATE BUSINESS CATEGORIES
# ------------------------------------------------

valid_categories = [
    "Cafe / Restaurant",
    "Retail Shop",
    "Gym / Fitness Center",
    "Pharmacy",
    "Salon / Beauty Center",
    "Electronics Store"
]

df = df[
    df["business_category"].isin(valid_categories)
].copy()

# ------------------------------------------------
# 7. VALIDATE MARKET POTENTIAL CATEGORY
# ------------------------------------------------

df["potential_category"] = np.where(
    df["market_potential_score"] >= 70,
    "High",
    np.where(
        df["market_potential_score"] >= 45,
        "Medium",
        "Low"
    )
)

# ------------------------------------------------
# 8. CHECK DATA QUALITY
# ------------------------------------------------

print("\nFinal missing values:")
print(df.isnull().sum())

print("\nFinal duplicate records:")
print(df.duplicated().sum())

print("\nFinal dataset shape:", df.shape)

print("\nPotential category distribution:")
print(df["potential_category"].value_counts())

# ------------------------------------------------
# 9. SAVE CLEANED DATASET
# ------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\n================================")
print("DATA PREPROCESSING COMPLETED")
print("================================")

print("Cleaned dataset saved at:")
print(OUTPUT_FILE)
