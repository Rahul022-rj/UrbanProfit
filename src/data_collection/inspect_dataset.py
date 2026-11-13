
import pandas as pd

# Load raw dataset
file_path = "data/raw/bengaluru_businesses_osm_v2.csv"
df = pd.read_csv(file_path)

print("\n" + "=" * 60)
print("URBANPROFIT - RAW DATASET INSPECTION")
print("=" * 60)

# 1. Dataset shape
print("\n1. DATASET SHAPE")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 2. Column names
print("\n2. COLUMN NAMES")
print(df.columns.tolist())

# 3. Data types
print("\n3. DATA TYPES")
print(df.dtypes)

# 4. Missing values
print("\n4. MISSING VALUES")
print(df.isnull().sum())

# 5. Duplicate records
print("\n5. DUPLICATE RECORDS")
print("Complete duplicate rows:", df.duplicated().sum())
print(
    "Duplicate OSM identities:",
    df.duplicated(subset=["element", "osmid"]).sum()
)

# 6. Category distribution
print("\n6. CATEGORY DISTRIBUTION")
print(df["business_category"].value_counts())

# 7. Locality distribution
print("\n7. LOCALITY DISTRIBUTION")
print(df["locality"].value_counts())

# 8. Coordinate validation
print("\n8. COORDINATE VALIDATION")
print("Latitude range:")
print(df["latitude"].min(), "to", df["latitude"].max())

print("Longitude range:")
print(df["longitude"].min(), "to", df["longitude"].max())

invalid_coordinates = df[
    ~df["latitude"].between(-90, 90)
    | ~df["longitude"].between(-180, 180)
]

print("Invalid coordinate records:", len(invalid_coordinates))

# 9. Sample records
print("\n9. FIRST 10 RECORDS")
print(df.head(10).to_string(index=False))

print("\n" + "=" * 60)
print("INSPECTION COMPLETED")
print("=" * 60)
