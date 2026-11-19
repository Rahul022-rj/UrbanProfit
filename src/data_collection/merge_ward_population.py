
import pandas as pd
import geopandas as gpd
from pathlib import Path

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

POPULATION_FILE = (
    "data/external/bengaluru_ward_population_2011.csv"
)

BOUNDARY_FILE = (
    "data/external/bengaluru_198_wards_2015.kml"
)

OUTPUT_FILE = Path(
    "data/processed/bengaluru_ward_population.geojson"
)

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

population = pd.read_csv(POPULATION_FILE)

wards = gpd.read_file(
    BOUNDARY_FILE,
    driver="KML"
)

print("\nURBANPROFIT - WARD POPULATION MERGING")
print("=" * 60)

# --------------------------------------------------
# 3. EXTRACT WARD NUMBER
# --------------------------------------------------

wards["Ward Num"] = (
    wards["Name"]
    .str.extract(r"(\d+)", expand=False)
    .astype(int)
)

# --------------------------------------------------
# 4. CHECK WARD IDENTIFIERS
# --------------------------------------------------

assert population["Ward Num"].is_unique, (
    "Duplicate population ward numbers found."
)

assert wards["Ward Num"].is_unique, (
    "Duplicate boundary ward numbers found."
)

assert set(population["Ward Num"]) == set(wards["Ward Num"]), (
    "Population and boundary ward numbers do not match."
)

# --------------------------------------------------
# 5. MERGE POPULATION AND GEOGRAPHY
# --------------------------------------------------

merged = wards.merge(
    population,
    on="Ward Num",
    how="inner",
    suffixes=("_boundary", "_population"),
    validate="one_to_one"
)

# Use the complete ward name from KML.
merged["Ward_Name"] = merged["Ward_Name"].str.strip()

# --------------------------------------------------
# 6. CALCULATE AREA
# --------------------------------------------------

# EPSG:32643 is UTM Zone 43N, suitable for Bengaluru.
projected = merged.to_crs(epsg=32643)

merged["area_sq_km"] = (
    projected.geometry.area / 1_000_000
)

# Population density based on 2011 population.
merged["population_density_2011"] = (
    merged["Population"] / merged["area_sq_km"]
)

# --------------------------------------------------
# 7. SAVE GEOJSON
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

merged = merged.to_crs(epsg=4326)

merged.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

# --------------------------------------------------
# 8. VALIDATION
# --------------------------------------------------

print("\nMerged records:", len(merged))

print("\nPopulation total:")
print(merged["Population"].sum())

print("\nAverage ward population:")
print(round(merged["Population"].mean(), 2))

print("\nAverage population density:")
print(round(
    merged["population_density_2011"].mean(), 2
), "people per sq km")

print("\nFirst 10 wards:")
print(
    merged[
        [
            "Ward Num",
            "Ward_Name",
            "Population",
            "area_sq_km",
            "population_density_2011"
        ]
    ].head(10).to_string(index=False)
)

print("\nSaved:", OUTPUT_FILE)

print("\nWARD POPULATION MERGING COMPLETED")
print("=" * 60)
