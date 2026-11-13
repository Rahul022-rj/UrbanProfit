
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Load dataset
INPUT_FILE = "data/processed/bengaluru_businesses_features.csv"
OUTPUT_DIR = Path("reports/eda")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

sns.set_theme(style="whitegrid")

print("\nURBANPROFIT - GEOGRAPHICAL ANALYSIS")
print("=" * 60)

# --------------------------------------------------
# 1. BUSINESS LOCATION SCATTER PLOT
# --------------------------------------------------

plt.figure(figsize=(10, 8))

sns.scatterplot(
    data=df,
    x="longitude",
    y="latitude",
    hue="business_category",
    alpha=0.6,
    s=25
)

plt.title("Geographical Distribution of Businesses in Bengaluru")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(
    title="Business Category",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "business_geographical_distribution.png",
    dpi=300
)
plt.show()

# --------------------------------------------------
# 2. CATEGORY-WISE COMPETITION
# --------------------------------------------------

competition = pd.crosstab(
    df["locality"],
    df["business_category"]
)

plt.figure(figsize=(12, 7))

sns.heatmap(
    competition,
    annot=True,
    fmt="d",
    cmap="OrRd"
)

plt.title("Category-wise Business Competition by Locality")
plt.xlabel("Business Category")
plt.ylabel("Locality")

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "competition_heatmap.png",
    dpi=300
)
plt.show()

# --------------------------------------------------
# 3. BUSINESS DENSITY PROXY
# --------------------------------------------------

# This is mapped business count per locality,
# not businesses per square kilometre.

density = (
    df.groupby("locality")
    .size()
    .reset_index(name="mapped_business_count")
    .sort_values(
        "mapped_business_count",
        ascending=False
    )
)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=density,
    x="mapped_business_count",
    y="locality"
)

plt.title("Mapped Business Count by Locality")
plt.xlabel("Mapped Business Count")
plt.ylabel("Locality")

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "locality_business_count.png",
    dpi=300
)
plt.show()

# --------------------------------------------------
# 4. NUMERICAL CORRELATION
# --------------------------------------------------

numeric_columns = [
    "latitude",
    "longitude",
    "total_locality_businesses",
    "business_count",
    "category_share",
    "has_name"
]

correlation = df[numeric_columns].corr()

plt.figure(figsize=(10, 7))

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    center=0
)

plt.title("Correlation Between Numerical Features")

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "numerical_correlation.png",
    dpi=300
)
plt.show()

# --------------------------------------------------
# 5. PRINT RESULTS
# --------------------------------------------------

print("\nLOCALITY BUSINESS COUNT")
print(density.to_string(index=False))

print("\nNUMERICAL CORRELATION")
print(correlation.round(2))

print("\nGEOGRAPHICAL ANALYSIS COMPLETED")
print("Charts saved in:", OUTPUT_DIR)
