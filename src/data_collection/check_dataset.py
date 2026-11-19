
import os
import pandas as pd

FILE_PATH = "data/raw/bengaluru_businesses_raw.csv"

print("\n========== URBANPROFIT DATASET CHECK ==========\n")

if not os.path.exists(FILE_PATH):
    print("ERROR: Dataset file not found!")
    print("Expected location:", FILE_PATH)
    raise SystemExit(1)

df = pd.read_csv(FILE_PATH)

print("1. DATASET INFORMATION")
print("-----------------------------------")
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Columns:", list(df.columns))

print("\n2. FIRST 10 RECORDS")
print("-----------------------------------")
print(df.head(10).to_string(index=False))

print("\n3. BUSINESS CATEGORY DISTRIBUTION")
print("-----------------------------------")

if "business_category" in df.columns:
    print(df["business_category"].value_counts(dropna=False))
else:
    print("business_category column is missing!")

print("\n4. LOCALITY DISTRIBUTION")
print("-----------------------------------")

if "locality" in df.columns:
    print(df["locality"].value_counts(dropna=False))
else:
    print("locality column is missing!")

print("\n5. MISSING VALUES")
print("-----------------------------------")
print(df.isnull().sum())

print("\n6. DUPLICATE RECORDS")
print("-----------------------------------")
print("Duplicates:", df.duplicated().sum())

print("\n7. DATASET SUMMARY")
print("-----------------------------------")
print(df.info())

print("\n========== CHECK COMPLETED ==========\n")
