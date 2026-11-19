
import geopandas as gpd
import pandas as pd

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

ward_file = (
    "data/processed/bengaluru_ward_population.geojson"
)

business_file = (
    "data/processed/bengaluru_businesses_features.csv"
)

wards = gpd.read_file(ward_file)

businesses = pd.read_csv(business_file)

# Convert business coordinates to GeoDataFrame
business_gdf = gpd.GeoDataFrame(
    businesses,
    geometry=gpd.points_from_xy(
        businesses["longitude"],
        businesses["latitude"]
    ),
    crs="EPSG:4326"
)

print("\nURBANPROFIT - LOCALITY COVERAGE CHECK")
print("=" * 60)

# --------------------------------------------------
# 2. ENSURE SAME CRS
# --------------------------------------------------

business_gdf = business_gdf.to_crs(wards.crs)

# --------------------------------------------------
# 3. CHECK BUSINESS POINTS INSIDE WARDS
# --------------------------------------------------

joined = gpd.sjoin(
    business_gdf,
    wards[["Ward Num", "Ward_Name", "geometry"]],
    how="left",
    predicate="within"
)

# --------------------------------------------------
# 4. LOCALITY COVERAGE
# --------------------------------------------------

coverage = (
    joined.groupby("locality")
    .agg(
        total_businesses=("osmid", "count"),
        businesses_inside_wards=("Ward Num", "count"),
        wards_covered=("Ward Num", "nunique")
    )
    .reset_index()
)

coverage["coverage_percentage"] = (
    coverage["businesses_inside_wards"]
    / coverage["total_businesses"]
) * 100

print("\nLOCALITY COVERAGE SUMMARY")
print(coverage.to_string(index=False))

# --------------------------------------------------
# 5. WARD DISTRIBUTION BY LOCALITY
# --------------------------------------------------

print("\nWARD DISTRIBUTION BY LOCALITY")

ward_distribution = (
    joined.dropna(subset=["Ward Num"])
    .groupby(["locality", "Ward Num", "Ward_Name"])
    .size()
    .reset_index(name="mapped_businesses")
)

print(ward_distribution.to_string(index=False))

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

coverage.to_csv(
    "data/processed/locality_ward_coverage.csv",
    index=False
)

ward_distribution.to_csv(
    "data/processed/locality_ward_distribution.csv",
    index=False
)

print("\nSaved:")
print("data/processed/locality_ward_coverage.csv")
print("data/processed/locality_ward_distribution.csv")

print("\nLOCALITY COVERAGE CHECK COMPLETED")
print("=" * 60)
