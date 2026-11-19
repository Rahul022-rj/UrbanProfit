
import pandas as pd
from datetime import date

FILE = "data/raw/urbanprofit_commercial_rent.csv"

records = [
    {
        "locality": "Koramangala",
        "listing_id": "KOR-001",
        "monthly_rent_inr": 60000,
        "area_sqft": 250,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-koramangala-bengaluru-MA4P5s2sntlyr4a7izpb",
    },
    {
        "locality": "Electronic City",
        "listing_id": "EC-001",
        "monthly_rent_inr": 16000,
        "area_sqft": 160,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-electronic-city-bengaluru-MA4P16rl894c0qkogx5",
    },
    {
        "locality": "Jayanagar",
        "listing_id": "JAY-001",
        "monthly_rent_inr": 30000,
        "area_sqft": 500,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-jayanagar-bengaluru-MA4P5vem1jmqfgn3h0vo",
    },
    {
        "locality": "HSR Layout",
        "listing_id": "HSR-001",
        "monthly_rent_inr": 40000,
        "area_sqft": 1100,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-hsr-layout-bengaluru-MA4P5kgp2umse63qjm62",
    },
    {
        "locality": "Whitefield",
        "listing_id": "WHI-001",
        "monthly_rent_inr": 20000,
        "area_sqft": 200,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-whitefield-bengaluru-MA4P4ie9y33s0tezykdb",
    },
    {
        "locality": "Marathahalli",
        "listing_id": "MAR-001",
        "monthly_rent_inr": 80000,
        "area_sqft": 1000,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-marathahalli-bengaluru-MA4P19pr5xnbnbzon4fz",
    },
    {
        "locality": "Malleshwaram",
        "listing_id": "MAL-001",
        "monthly_rent_inr": 40000,
        "area_sqft": 500,
        "source_url": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-malleswaram-bengaluru-MA4P53twp7mtetscn6n9",
    }
]

df = pd.read_csv(FILE)

new_df = pd.DataFrame(records)

new_df["rent_per_sqft"] = (
    new_df["monthly_rent_inr"] / new_df["area_sqft"]
)

new_df["property_type"] = "Shop"
new_df["source_name"] = "Housing.com"
new_df["collection_date"] = date.today().isoformat()
new_df["listing_date"] = None
new_df["notes"] = (
    "Preliminary asking-rent observation; verify listing "
    "availability and property details before final analysis."
)

# Keep existing observations if script is run again.
combined = pd.concat([df, new_df], ignore_index=True)
combined = combined.drop_duplicates(
    subset=["listing_id"],
    keep="first"
)

combined.to_csv(FILE, index=False)

print("Initial rent observations saved.")
print(
    combined[
        ["locality", "monthly_rent_inr",
         "area_sqft", "rent_per_sqft"]
    ].to_string(index=False)
)
print("\nTotal records:", len(combined))
print("Saved:", FILE)
