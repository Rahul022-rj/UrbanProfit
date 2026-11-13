
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data" / "raw"
    / "urbanprofit_commercial_rent.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "external"
    / "urbanprofit_rent_collection_sheet.csv"
)

LOCALITIES = [
    "Koramangala",
    "Electronic City",
    "Jayanagar",
    "HSR Layout",
    "Indiranagar",
    "Whitefield",
    "Marathahalli",
    "Malleshwaram"
]

COLUMNS = [
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


def main():

    print("=" * 60)
    print("URBANPROFIT - RENT COLLECTION SHEET")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    existing = pd.read_csv(INPUT_FILE)

    # Check required columns
    missing = [
        col for col in COLUMNS
        if col not in existing.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Keep existing real listings
    existing = existing[COLUMNS].copy()

    if existing["listing_id"].duplicated().any():
        raise ValueError("Duplicate listing IDs found.")

    rows = []

    for locality in LOCALITIES:

        locality_data = existing[
            existing["locality"] == locality
        ]

        # Preserve existing records
        for _, record in locality_data.iterrows():
            rows.append(record.to_dict())

        current_count = len(locality_data)

        # Prepare blank slots until 5 listings
        for number in range(current_count + 1, 6):

            rows.append({
                "locality": locality,
                "listing_id": "",
                "property_type": "",
                "monthly_rent_inr": "",
                "area_sqft": "",
                "rent_per_sqft": "",
                "source_url": "",
                "source_name": "",
                "listing_date": "",
                "collection_date": "",
                "notes": f"Enter listing {number}"
            })

    result = pd.DataFrame(rows, columns=COLUMNS)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(OUTPUT_FILE, index=False)

    print("\nExisting listings:", len(existing))
    print("Target listings:", len(LOCALITIES) * 5)
    print("Collection slots:", len(result))

    print("\nCurrent listing count:")
    print(
        existing.groupby("locality")
        .size()
        .reindex(LOCALITIES, fill_value=0)
    )

    print("\nSaved collection sheet:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
