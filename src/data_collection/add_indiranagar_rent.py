
import pandas as pd
from datetime import date

FILE = "data/raw/urbanprofit_commercial_rent.csv"

df = pd.read_csv(FILE)

record = {
    "locality": "Indiranagar",
    "listing_id": "100478069",
    "property_type": "Shop",
    "monthly_rent_inr": 35000,
    "area_sqft": 600,
    "rent_per_sqft": 35000 / 600,
    "source_url": "https://housing.com/commercial/rent/100478069-shop-for-rent-in-indira-nagar-bangalore-for-rs-35000",
    "source_name": "Housing.com",
    "listing_date": "2026-09-23",
    "collection_date": date.today().isoformat(),
    "notes": "Motappana Palya; built-up area 600 sqft; asking rent."
}

new_record = pd.DataFrame([record])

df = pd.concat([df, new_record], ignore_index=True)

df = df.drop_duplicates(
    subset=["listing_id"],
    keep="first"
)

df.to_csv(FILE, index=False)

print("Indiranagar listing added.")
print(df[df["locality"] == "Indiranagar"].to_string(index=False))
print("\nTotal listings:", len(df))
