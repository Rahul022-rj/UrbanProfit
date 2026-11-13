
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data/processed/urbanprofit_market_scores.csv"
OUTPUT_FILE = ROOT / "data/processed/urbanprofit_locality_clusters.csv"

# Load data
df = pd.read_csv(INPUT_FILE)

# Features for clustering
features = [
    "population_density",
    "commercial_rent_per_sqft",
    "road_density_km_per_sq_km",
    "total_mapped_businesses"
]

# Validate features
X = df[features].apply(pd.to_numeric, errors="coerce")

if X.isnull().any().any():
    raise ValueError("Missing or invalid values in clustering features.")

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply K-Means
kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(X_scaled)

# Evaluate clustering
score = silhouette_score(X_scaled, df["cluster"])

# Create cluster profiles
profile = df.groupby("cluster")[features].mean().round(2)

# Save outputs
df.to_csv(OUTPUT_FILE, index=False)

print("\nURBANPROFIT K-MEANS CLUSTERING")
print("=" * 50)

print("\nLocality cluster assignments:")
print(
    df[["locality", "cluster", "market_potential_score"]]
    .sort_values("cluster")
    .to_string(index=False)
)

print("\nCluster profiles:")
print(profile)

print("\nSilhouette Score:", round(score, 3))

print("\nSaved:", OUTPUT_FILE)
