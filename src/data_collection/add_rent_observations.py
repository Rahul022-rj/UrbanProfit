

import pandas as pd
from pathlib import Path
from datetime import date

# Project root
ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "raw" / "urbanprofit_commercial_rent.csv"

# Housing.com locality search pages
SOURCES = {
    "Koramangala": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-koramangala-bengaluru-MA4P5s2sntlyr4a7izpb",
    "Electronic City": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-electronic-city-bengaluru-MA4P16rl894c0qkogx5",
    "Jayanagar": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-jayanagar-bengaluru-MA4P5vem1jmqfgn3h0vo",
    "HSR Layout": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-hsr-layout-bengaluru-MA4P5kgp2umse63qjm62",
    "Indiranagar": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-indira-nagar-bengaluru-MA4Pu0r6m95i80gbhpp",
    "Whitefield": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-whitefield-bengaluru-MA4P4ie9y33s0tezykdb",
    "Marathahalli": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-marathahalli-bengaluru-MA4P19pr5xnbnbzon4fz",
    "Malleshwaram": "https://housing.com/commercial/rent/commercial-shop-for-rent-in-malleswaram-bengaluru-MA4P53twp7mtetscn6n9"
}

# Preliminary observations from the search-result summary.
# Verify each individual listing before final submission.
observations = [
    ("Koramangala", 23000, 100),
    ("Koramangala", 50000, 1250),
    ("Koramangala", 25000, 100),

    ("Electronic City", 6500, 240),
    ("Electronic City", 25000, 240),
    ("Electronic City", 7000, 250),
    ("Electronic City", 75000, 1150),

    ("Jayanagar", 15500, 100),

    ("HSR Layout", 40000, 1200),

    ("Indiranagar", 18000, 200),
    ("Indiranagar", 50000, 700),
    ("Indiranagar", 35000, 600),

    ("Whitefield", 11000, 200),
    ("Whitefield", 17000, 170),

    ("Marathahalli", 10000, 250),
    ("Marathahalli", 15000, 80),

    ("Malleshwaram", 35000, 500),
]

# Read existing dataset
df = pd.read_csv(INPUT_FILE)

required_columns = [
    "locality", "listing_id", "property_type",
    "monthly_rent_inr", "area_sqft", "rent_per_sqft",
    "source_url", "source_name", "listing_date",
    "collection_date", "notes"
]

for column in required_columns:
    if column not in df.columns:
        df[column] = ""

added = 0
skipped = 0

for locality, rent, area in observations:

    # Avoid adding an existing locality/rent/area combination
    duplicate = (
        (df["locality"].astype(str) == locality)
        & (pd.to_numeric(df["monthly_rent_inr"], errors="coerce") == rent)
        & (pd.to_numeric(df["area_sqft"], errors="coerce") == area)
    ).any()

    if duplicate:
        skipped += 1
        continue

    new_record = {
        "locality": locality,
        "listing_id": "",
        "property_type": "Shop",
        "monthly_rent_inr": rent,
        "area_sqft": area,
        "rent_per_sqft": round(rent / area, 2),
        "source_url": SOURCES[locality],
        "source_name": "Housing.com",
        "listing_date": "",
        "collection_date": date.today().isoformat(),
        "notes": (
            "Preliminary search-result observation. "
            "Verify individual listing, availability, "
            "rent and area before final analysis."
        )
    }

    df = pd.concat(
        [df, pd.DataFrame([new_record])],
        ignore_index=True
    )
    added += 1

# Save updated dataset
df = df[required_columns]
df.to_csv(INPUT_FILE, index=False)

print("\nRENT DATA UPDATE COMPLETE")
print("--------------------------------")
print("New records added:", added)
print("Duplicates skipped:", skipped)
print("Total records:", len(df))

print("\nRecords per locality:")
print(df.groupby("locality").size())

print("\nUpdated file:")
print(INPUT_FILE)
