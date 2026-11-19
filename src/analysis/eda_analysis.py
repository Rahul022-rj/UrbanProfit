
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

INPUT_FILE = "data/processed/bengaluru_businesses_features.csv"

OUTPUT_DIR = Path("reports/eda")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

sns.set_theme(style="whitegrid")

print("\nURBANPROFIT - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# --------------------------------------------------
# 2. CATEGORY DISTRIBUTION
# --------------------------------------------------

category_counts = df["business_category"].value_counts()

plt.figure(figsize=(10, 6))
sns.barplot(
    x=category_counts.values,
    y=category_counts.index
)

plt.title("Business Category Distribution")
plt.xlabel("Number of Businesses")
plt.ylabel("Business Category")
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "category_distribution.png", dpi=300)
plt.show()

# --------------------------------------------------
# 3. LOCALITY DISTRIBUTION
# --------------------------------------------------

locality_counts = df["locality"].value_counts()

plt.figure(figsize=(10, 6))
sns.barplot(
    x=locality_counts.values,
    y=locality_counts.index
)

plt.title("Business Distribution Across Localities")
plt.xlabel("Number of Businesses")
plt.ylabel("Locality")
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "locality_distribution.png", dpi=300)
plt.show()

# --------------------------------------------------
# 4. CATEGORY-WISE LOCALITY COMPARISON
# --------------------------------------------------

pivot_data = pd.crosstab(
    df["locality"],
    df["business_category"]
)

plt.figure(figsize=(12, 7))

sns.heatmap(
    pivot_data,
    annot=True,
    fmt="d",
    cmap="YlGnBu"
)

plt.title("Business Category vs Locality")
plt.xlabel("Business Category")
plt.ylabel("Locality")
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "category_locality_heatmap.png", dpi=300)
plt.show()

# --------------------------------------------------
# 5. BUSINESS NAME AVAILABILITY
# --------------------------------------------------

name_counts = df["has_name"].value_counts().sort_index()

plt.figure(figsize=(7, 5))

sns.barplot(
    x=["Missing Name", "Name Available"],
    y=[name_counts.get(0, 0), name_counts.get(1, 0)]
)

plt.title("Business Name Availability")
plt.xlabel("Name Status")
plt.ylabel("Number of Businesses")
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "business_name_availability.png", dpi=300)
plt.show()

# --------------------------------------------------
# 6. STATISTICAL SUMMARY
# --------------------------------------------------

print("\n1. TOTAL BUSINESSES")
print(len(df))

print("\n2. CATEGORY DISTRIBUTION")
print(category_counts)

print("\n3. LOCALITY DISTRIBUTION")
print(locality_counts)

print("\n4. CATEGORY VS LOCALITY")
print(pivot_data)

print("\n5. BUSINESS NAME AVAILABILITY")
print("Named:", int((df["has_name"] == 1).sum()))
print("Unnamed:", int((df["has_name"] == 0).sum()))

print("\n6. CATEGORY SHARE SUMMARY")
print(
    df.groupby(["locality", "business_category"])["category_share"]
    .first()
    .round(2)
)

print("\nEDA completed successfully.")
print("Charts saved in:", OUTPUT_DIR)
