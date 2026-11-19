
import pandas as pd

file_path = "data/external/bengaluru_ward_population_2011.csv"

df = pd.read_csv(file_path)

print("\nBENGALURU WARD POPULATION DATA")
print("=" * 55)

print("\nDataset shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nFirst 10 records:")
print(df.head(10).to_string(index=False))

print("\nPopulation summary:")
print(df.describe(include="all").to_string())

print("\nInspection completed.")
