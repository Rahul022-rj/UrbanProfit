
import pandas as pd
import geopandas as gpd

# Load datasets
businesses = pd.read_csv(
    "data/processed/bengaluru_businesses_features.csv"
)

wards = gpd.read_file(
    "data/processed/bengaluru_ward_population.geojson"
)

# Convert businesses into geographic points
business_gdf = gpd.GeoDataFrame(
    businesses,
    geometry=gpd.points_from_xy(
        businesses["longitude"],
        businesses["latitude"]
    ),
    crs="EPSG:4326"
)

# Select Electronic City records
electronic_city = business_gdf[
    business_gdf["locality"] == "Electronic City"
].copy()

# Match coordinate systems
electronic_city = electronic_city.to_crs(wards.crs)

# Check whether each point is inside the BBMP boundary
joined = gpd.sjoin(
    electronic_city,
    wards[["Ward Num", "Ward_Name", "geometry"]],
    how="left",
    predicate="within"
)

# Separate inside and outside records
inside = joined[joined["Ward Num"].notna()]
outside = joined[joined["Ward Num"].isna()]

print("\nELECTRONIC CITY GEOGRAPHICAL INVESTIGATION")
print("=" * 60)

print("\nTotal Electronic City businesses:", len(joined))
print("Inside BBMP wards:", len(inside))
print("Outside BBMP wards:", len(outside))

print("\nElectronic City coordinate ranges:")

print(
    "Latitude:",
    electronic_city["latitude"].min(),
    "to",
    electronic_city["latitude"].max()
)

print(
    "Longitude:",
    electronic_city["longitude"].min(),
    "to",
    electronic_city["longitude"].max()
)

print("\nBusinesses inside wards:")

print(
    inside[
        ["name", "business_category", "Ward Num", "Ward_Name"]
    ].head(10).to_string(index=False)
)

# Save outside records for inspection
outside.drop(columns=["index_right"], errors="ignore").to_csv(
    "data/processed/electronic_city_outside_bbmp.csv",
    index=False
)

print("\nOutside records saved:")
print("data/processed/electronic_city_outside_bbmp.csv")

print("\nINVESTIGATION COMPLETED")
print("=" * 60)
