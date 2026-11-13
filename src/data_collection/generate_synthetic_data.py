
import os
import numpy as np
import pandas as pd

# Reproducible synthetic dataset
np.random.seed(42)

OUTPUT_DIR = "data/synthetic"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "urbanprofit_market_data_synthetic.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

localities = {
    "Koramangala": 0.95,
    "Indiranagar": 0.92,
    "Whitefield": 0.88,
    "Electronic City": 0.82,
    "Jayanagar": 0.86,
    "Malleshwaram": 0.78,
    "HSR Layout": 0.90,
    "Marathahalli": 0.85
}

categories = [
    "Cafe / Restaurant",
    "Retail Shop",
    "Gym / Fitness Center",
    "Pharmacy",
    "Salon / Beauty Center",
    "Electronics Store"
]

records = []

for locality, area_factor in localities.items():

    for category in categories:

        for i in range(25):

            population_density = np.random.randint(
                4000, 25000
            )

            competitor_count = np.random.randint(
                1, 80
            )

            existing_business_count = np.random.randint(
                10, 250
            )

            avg_monthly_rent = np.random.randint(
                12000, 100001
            )

            distance_main_road_km = round(
                np.random.uniform(0.1, 5.0), 2
            )

            transport_access_score = np.random.randint(
                20, 101
            )

            income_index = np.random.randint(
                25, 101
            )

            footfall_index = np.random.randint(
                20, 101
            )

            # Normalize features to 0-100
            population_score = np.clip(
                population_density / 25000 * 100,
                0, 100
            )

            competition_score = np.clip(
                100 - competitor_count / 80 * 100,
                0, 100
            )

            rent_score = np.clip(
                100 - avg_monthly_rent / 100000 * 100,
                0, 100
            )

            road_score = np.clip(
                100 - distance_main_road_km / 5 * 100,
                0, 100
            )

            business_density_score = np.clip(
                existing_business_count / 250 * 100,
                0, 100
            )

            # Synthetic market potential formula
            score = (
                0.20 * population_score
                + 0.20 * competition_score
                + 0.15 * rent_score
                + 0.10 * road_score
                + 0.10 * transport_access_score
                + 0.10 * income_index
                + 0.10 * footfall_index
                + 0.05 * business_density_score
            )

            # Locality adjustment and random variation
            score = (
                score * (0.85 + 0.15 * area_factor)
                + np.random.normal(0, 4)
            )

            score = round(
                float(np.clip(score, 0, 100)), 2
            )

            if score >= 70:
                potential_category = "High"
            elif score >= 45:
                potential_category = "Medium"
            else:
                potential_category = "Low"

            records.append({
                "locality": locality,
                "business_category": category,
                "population_density": population_density,
                "competitor_count": competitor_count,
                "existing_business_count": existing_business_count,
                "avg_monthly_rent": avg_monthly_rent,
                "distance_main_road_km": distance_main_road_km,
                "transport_access_score": transport_access_score,
                "income_index": income_index,
                "footfall_index": footfall_index,
                "market_potential_score": score,
                "potential_category": potential_category,
                "data_source": "Synthetic"
            })

# Create DataFrame
df = pd.DataFrame(records)

# Save dataset
df.to_csv(OUTPUT_FILE, index=False)

print("\n================================")
print("URBANPROFIT SYNTHETIC DATA READY")
print("================================")

print("\nDataset shape:", df.shape)

print("\nBusiness category distribution:")
print(df["business_category"].value_counts())

print("\nPotential category distribution:")
print(df["potential_category"].value_counts())

print("\nLocality distribution:")
print(df["locality"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())

print("\nFirst 5 records:")
print(df.head())

print("\nSaved successfully:")
print(OUTPUT_FILE)
