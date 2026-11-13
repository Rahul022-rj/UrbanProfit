
import pandas as pd
import geopandas as gpd
import re

# --------------------------------------------------
# 1. LOAD BOTH DATASETS
# --------------------------------------------------

POPULATION_FILE = (
    "data/external/bengaluru_ward_population_2011.csv"
)

BOUNDARY_FILE = (
    "data/external/bengaluru_198_wards_2015.kml"
)

population = pd.read_csv(POPULATION_FILE)

wards = gpd.read_file(
    BOUNDARY_FILE,
    driver="KML"
)

print("\nURBANPROFIT - WARD POPULATION MATCHING")
print("=" * 60)

# --------------------------------------------------
# 2. NORMALIZE WARD NAMES
# --------------------------------------------------

def normalize_name(name):
    name = str(name).lower().strip()
    name = re.sub(r"\bward\b", "", name)
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


population["normalized_name"] = (
    population["Ward Name"].apply(normalize_name)
)

wards["normalized_name"] = (
    wards["Ward_Name"].apply(normalize_name)
)

# --------------------------------------------------
# 3. EXTRACT WARD NUMBER FROM KML
# --------------------------------------------------

wards["Ward Num"] = (
    wards["Name"]
    .str.extract(r"(\d+)", expand=False)
    .astype(int)
)

# --------------------------------------------------
# 4. CHECK DUPLICATES
# --------------------------------------------------

print("\nPopulation ward count:", len(population))
print("Boundary ward count:", len(wards))

print(
    "Duplicate population ward numbers:",
    population["Ward Num"].duplicated().sum()
)

print(
    "Duplicate boundary ward numbers:",
    wards["Ward Num"].duplicated().sum()
)

# --------------------------------------------------
# 5. MATCH BY WARD NUMBER
# --------------------------------------------------

matched = population.merge(
    wards[
        [
            "Ward Num",
            "Ward_Name",
            "normalized_name",
            "geometry"
        ]
    ],
    on="Ward Num",
    how="outer",
    suffixes=("_population", "_boundary"),
    indicator=True
)

print("\nWARD NUMBER MATCH STATUS")
print(matched["_merge"].value_counts())

# --------------------------------------------------
# 6. CHECK WARD NAME MATCHES
# --------------------------------------------------

matched["name_match"] = (
    matched["normalized_name_population"]
    == matched["normalized_name_boundary"]
)

print(
    "\nWard names matching:",
    matched["name_match"].sum()
)

print(
    "Ward names not matching:",
    (~matched["name_match"]).sum()
)

print("\nUNMATCHED WARD NAMES:")

unmatched = matched[
    (matched["_merge"] != "both")
    | (~matched["name_match"])
]

print(
    unmatched[
        [
            "Ward Num",
            "Ward Name",
            "Ward_Name",
            "_merge",
            "name_match"
        ]
    ].to_string(index=False)
)

print("\nWARD MATCHING INSPECTION COMPLETED")
print("=" * 60)
