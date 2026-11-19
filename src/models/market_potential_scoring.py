
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data/processed/urbanprofit_market_dataset_final.csv"
OUTPUT_FILE = ROOT / "data/processed/urbanprofit_market_scores.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

# Features used in the model
features = [
    "population_density",
    "road_density_km_per_sq_km",
    "commercial_rent_per_sqft",
    "total_mapped_businesses"
]

# Check missing values
if df[features].isnull().any().any():
    raise ValueError(
        "Missing values found in scoring features. "
        "Check the dataset before scoring."
    )

# Convert features to numeric
for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df[features].isnull().any().any():
    raise ValueError("Some scoring features are not numeric.")

# Normalize features to 0-1
scaler = MinMaxScaler()

normalized = pd.DataFrame(
    scaler.fit_transform(df[features]),
    columns=features,
    index=df.index
)

# Positive indicators: higher values are better
population_score = normalized["population_density"]
road_score = normalized["road_density_km_per_sq_km"]

# Negative indicators: lower values are better
rent_score = 1 - normalized["commercial_rent_per_sqft"]
competition_score = 1 - normalized["total_mapped_businesses"]

# Calculate weighted score
df["population_score"] = population_score * 100
df["road_accessibility_score"] = road_score * 100
df["rent_affordability_score"] = rent_score * 100
df["competition_score"] = competition_score * 100

df["market_potential_score"] = (
    population_score * 0.30
    + road_score * 0.25
    + rent_score * 0.20
    + competition_score * 0.25
) * 100

# Rank localities
df["market_rank"] = (
    df["market_potential_score"]
    .rank(method="dense", ascending=False)
    .astype(int)
)

# Assign descriptive categories
def classify_score(score):
    if score >= 70:
        return "High Potential"
    elif score >= 40:
        return "Moderate Potential"
    else:
        return "Low Potential"

df["potential_category"] = df[
    "market_potential_score"
].apply(classify_score)

# Sort by score
df = df.sort_values(
    "market_potential_score",
    ascending=False
)

# Save results
df.to_csv(OUTPUT_FILE, index=False)

print("\nURBANPROFIT MARKET POTENTIAL RESULTS")
print("=" * 55)

print(df[[
    "locality",
    "market_potential_score",
    "market_rank",
    "potential_category"
]].round(2).to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
