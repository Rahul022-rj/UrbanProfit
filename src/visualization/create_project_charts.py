
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FILE = ROOT / "data/processed/urbanprofit_locality_clusters.csv"
OUTPUT = ROOT / "reports/visualizations"

OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(FILE)

# 1. Market Potential Ranking
data = df.sort_values("market_potential_score")

plt.figure(figsize=(10, 6))
plt.barh(data["locality"], data["market_potential_score"])
plt.xlabel("Market Potential Score (0-100)")
plt.ylabel("Locality")
plt.title("UrbanProfit - Market Potential Ranking")
plt.tight_layout()
plt.savefig(OUTPUT / "market_potential_ranking.png", dpi=300)
plt.close()

# 2. K-Means Clustering
plt.figure(figsize=(9, 6))

for cluster in sorted(df["cluster"].unique()):
    subset = df[df["cluster"] == cluster]
    plt.scatter(
        subset["population_density"],
        subset["commercial_rent_per_sqft"],
        label=f"Cluster {cluster}",
        s=100
    )

for _, row in df.iterrows():
    plt.annotate(
        row["locality"],
        (row["population_density"], row["commercial_rent_per_sqft"]),
        fontsize=8
    )

plt.xlabel("Population Density (people/km²)")
plt.ylabel("Commercial Rent (₹/sq.ft./month)")
plt.title("UrbanProfit - K-Means Locality Clusters")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT / "locality_clusters.png", dpi=300)
plt.close()

# 3. Population vs Competition
plt.figure(figsize=(9, 6))
plt.scatter(
    df["population_density"],
    df["total_mapped_businesses"],
    s=100
)

for _, row in df.iterrows():
    plt.annotate(
        row["locality"],
        (row["population_density"], row["total_mapped_businesses"]),
        fontsize=8
    )

plt.xlabel("Population Density (people/km²)")
plt.ylabel("Mapped Business Count")
plt.title("Population Density vs Competition")
plt.tight_layout()
plt.savefig(OUTPUT / "population_vs_competition.png", dpi=300)
plt.close()

# 4. Commercial Rent Comparison
data = df.sort_values("commercial_rent_per_sqft")

plt.figure(figsize=(10, 6))
plt.barh(
    data["locality"],
    data["commercial_rent_per_sqft"]
)
plt.xlabel("Median Asking Rent (₹/sq.ft./month)")
plt.ylabel("Locality")
plt.title("Commercial Rent Comparison")
plt.tight_layout()
plt.savefig(OUTPUT / "commercial_rent_comparison.png", dpi=300)
plt.close()

print("\nALL PROJECT CHARTS CREATED")
print("Output folder:", OUTPUT)

for file in OUTPUT.glob("*.png"):
    print(file.name)
