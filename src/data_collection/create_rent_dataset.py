
import os
import pandas as pd

OUTPUT_FILE = "data/raw/urbanprofit_commercial_rent.csv"

columns = [
    "locality",
    "listing_id",
    "property_type",
    "monthly_rent_inr",
    "area_sqft",
    "rent_per_sqft",
    "source_url",
    "source_name",
    "listing_date",
    "collection_date",
    "notes"
]

df = pd.DataFrame(columns=columns)

os.makedirs("data/raw", exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

print("Listing-level rent dataset created.")
print("Columns:", list(df.columns))
print("Saved:", OUTPUT_FILE)
