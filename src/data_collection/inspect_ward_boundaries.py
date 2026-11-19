
import geopandas as gpd
from pathlib import Path

# --------------------------------------------------
# 1. FILE PATH
# --------------------------------------------------

FILE_PATH = Path(
    "data/external/bengaluru_198_wards_2015.kml"
)

print("\nURBANPROFIT - WARD BOUNDARY INSPECTION")
print("=" * 60)

# --------------------------------------------------
# 2. CHECK FILE
# --------------------------------------------------

if not FILE_PATH.exists():
    raise FileNotFoundError(
        f"KML file not found: {FILE_PATH}"
    )

# --------------------------------------------------
# 3. READ KML
# --------------------------------------------------

gdf = gpd.read_file(FILE_PATH, driver="KML")

# --------------------------------------------------
# 4. DATASET INFORMATION
# --------------------------------------------------

print("\nDataset shape:", gdf.shape)

print("\nColumn names:")
print(gdf.columns.tolist())

print("\nCoordinate Reference System:")
print(gdf.crs)

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

print("\nMissing values:")
print(gdf.isnull().sum())

# --------------------------------------------------
# 5. WARD NAMES
# --------------------------------------------------

print("\nFirst 20 ward records:")

display_columns = [
    col for col in gdf.columns
    if col != "geometry"
]

print(gdf[display_columns].head(20).to_string(index=False))

# --------------------------------------------------
# 6. GEOGRAPHICAL BOUNDS
# --------------------------------------------------

print("\nGeographical bounds:")
print(gdf.total_bounds)

# --------------------------------------------------
# 7. GEOMETRY VALIDATION
# --------------------------------------------------

print("\nEmpty geometries:", gdf.geometry.is_empty.sum())

print("Invalid geometries:", (~gdf.geometry.is_valid).sum())

print(
    "\nUnique ward records:",
    len(gdf)
)

print("\nWARD BOUNDARY INSPECTION COMPLETED")
print("=" * 60)
