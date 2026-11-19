
import os
import time
from datetime import datetime, timezone

import osmnx as ox
import pandas as pd


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

OUTPUT_DIR = "data/raw"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "bengaluru_businesses_osm_v2.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.requests_timeout = 180

# Keep the requests manageable by collecting one locality at a time.
AREAS = [
    "Koramangala, Bengaluru, India",
    "Electronic City, Bengaluru, India",
    "Jayanagar, Bengaluru, India"
]
# Approximate locality centres: latitude, longitude
LOCALITY_CENTERS = {
    "Koramangala": (12.9352, 77.6245),
    "Electronic City": (12.8399, 77.6770),
    "Jayanagar": (12.9250, 77.5838)
}

SEARCH_RADIUS = 3000  # 3 kilometres
TAGS = {
    "amenity": [
        "cafe",
        "restaurant",
        "fast_food",
        "pharmacy"
    ],
    "shop": [
        "supermarket",
        "convenience",
        "department_store",
        "clothes",
        "electronics",
        "hairdresser",
        "beauty"
    ],
    "leisure": [
        "fitness_centre"
    ]
}

COLUMNS = [
    "element",
    "osmid",
    "name",
    "business_category",
    "amenity",
    "shop",
    "leisure",
    "latitude",
    "longitude",
    "addr:street",
    "addr:suburb",
    "addr:city",
    "locality",
    "source",
    "collected_at_utc"
]


# --------------------------------------------------
# 2. CATEGORY CLASSIFICATION
# --------------------------------------------------

def classify_business(row):

    amenity = str(row.get("amenity", "")).lower()
    shop = str(row.get("shop", "")).lower()
    leisure = str(row.get("leisure", "")).lower()

    if amenity in ["cafe", "restaurant", "fast_food"]:
        return "Cafe / Restaurant"

    if amenity == "pharmacy":
        return "Pharmacy"

    if leisure == "fitness_centre":
        return "Gym / Fitness Center"

    if shop in [
        "supermarket",
        "convenience",
        "department_store",
        "clothes"
    ]:
        return "Retail Shop"

    if shop in ["hairdresser", "beauty"]:
        return "Salon / Beauty Center"

    if shop == "electronics":
        return "Electronics Store"

    return None


# --------------------------------------------------
# 3. SAFE VALUE EXTRACTION
# --------------------------------------------------

def clean_value(value):

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    if pd.isna(value):
        return None

    return str(value)


# --------------------------------------------------
# 4. CONVERT OSM FEATURES INTO DATAFRAME
# --------------------------------------------------

def process_features(gdf, locality):

    if gdf.empty:
        return pd.DataFrame(columns=COLUMNS)

    # OSMnx features commonly use a MultiIndex:
    # element + id. Reset it to obtain the OSM identifier.
    gdf = gdf.reset_index()

    if "id" in gdf.columns:
        gdf = gdf.rename(columns={"id": "osmid"})

    if "osmid" not in gdf.columns:
        print("WARNING: OSM ID column not found.")
        return pd.DataFrame(columns=COLUMNS)

    # Convert geometry to latitude/longitude coordinates.
    if gdf.crs is not None:
        gdf = gdf.to_crs(epsg=4326)

    records = []

    for _, row in gdf.iterrows():

        category = classify_business(row)

        if category is None:
            continue

        geometry = row.geometry

        if geometry is None or geometry.is_empty:
            continue

        # Representative point works for both points
        # and polygon/line geometries.
        point = geometry.representative_point()

        record = {
            "element": clean_value(row.get("element")),
            "osmid": clean_value(row.get("osmid")),
            "name": clean_value(row.get("name")),
            "business_category": category,
            "amenity": clean_value(row.get("amenity")),
            "shop": clean_value(row.get("shop")),
            "leisure": clean_value(row.get("leisure")),
            "latitude": point.y,
            "longitude": point.x,
            "addr:street": clean_value(row.get("addr:street")),
            "addr:suburb": clean_value(row.get("addr:suburb")),
            "addr:city": clean_value(row.get("addr:city")),
            "locality": locality,
            "source": "OpenStreetMap",
            "collected_at_utc": datetime.now(
                timezone.utc
            ).isoformat()
        }

        records.append(record)

    return pd.DataFrame(records, columns=COLUMNS)


# --------------------------------------------------
# 5. SAVE DATA WITH OSM ID DEDUPLICATION
# --------------------------------------------------

def save_progress(data):

    if data.empty:
        print("No records to save.")
        return

    output_file = "data/raw/bengaluru_businesses_osm_v2.csv"

    # Ensure the output directory exists.
    os.makedirs("data/raw", exist_ok=True)

    # Load existing records if the file exists.
    if os.path.exists(output_file):

        existing = pd.read_csv(output_file)

        combined = pd.concat(
            [existing, data],
            ignore_index=True
        )

    else:

        combined = data.copy()

    # Normalize OSM identifiers.
    combined["osmid"] = combined["osmid"].astype("string").str.strip()
    combined["element"] = combined["element"].astype("string").str.strip()

    # Remove duplicates using the OSM element type and ID.
    # This avoids incorrectly merging a node and a way
    # that happen to have the same numeric ID.
    valid_ids = (
        combined["osmid"].notna()
        & combined["osmid"].ne("")
        & combined["osmid"].ne("nan")
    )

    identified = combined[valid_ids].drop_duplicates(
        subset=["element", "osmid"],
        keep="first"
    )

    unidentified = combined[~valid_ids]

    combined = pd.concat(
        [identified, unidentified],
        ignore_index=True
    )

    # Save final dataset.
    combined.to_csv(output_file, index=False)

    print("Saved progress:", len(combined), "records")


# --------------------------------------------------
# 6. COLLECT ONE LOCALITY WITH POLYGON + COORDINATE FALLBACK
# --------------------------------------------------

def collect_locality(place, max_retries=3):

    locality = place.split(",")[0]

    print("\n" + "=" * 60)
    print(f"COLLECTING: {locality}")
    print("=" * 60)

    coordinates = LOCALITY_CENTERS.get(locality)

    for attempt in range(1, max_retries + 1):

        print(f"\nAttempt {attempt}/{max_retries}")

        # ------------------------------------------
        # METHOD 1: POLYGON-BASED COLLECTION
        # ------------------------------------------

        try:

            print("Trying polygon-based search...")

            gdf = ox.features_from_place(
                place,
                tags=TAGS
            )

            if gdf.empty:
                raise ValueError("No matching OSM features found.")

            print("OSM features received:", len(gdf))

            data = process_features(gdf, locality)

            print("Business records extracted:", len(data))

            if not data.empty:
                save_progress(data)

            print(f"SUCCESS: {locality} collected using polygon search.")

            return len(data)

        except Exception as polygon_error:

            print("Polygon search failed:", str(polygon_error))

        # ------------------------------------------
        # METHOD 2: COORDINATE-BASED FALLBACK
        # ------------------------------------------

        if coordinates is None:

            print("No coordinates configured for:", locality)
            break

        try:

            print("Trying coordinate-based search...")
            print("Centre:", coordinates)
            print("Search radius:", SEARCH_RADIUS, "metres")

            gdf = ox.features_from_point(
                coordinates,
                tags=TAGS,
                dist=SEARCH_RADIUS
            )

            print("OSM features received:", len(gdf))

            if gdf.empty:
                raise ValueError("No matching features in coordinate search.")

            data = process_features(gdf, locality)

            print("Business records extracted:", len(data))

            if data.empty:
                raise ValueError("No valid business records after processing.")

            save_progress(data)

            print(f"SUCCESS: {locality} collected using coordinate search.")

            return len(data)

        except Exception as coordinate_error:

            print("Coordinate search failed:", str(coordinate_error))

            if attempt < max_retries:

                wait_time = 2 ** attempt

                print(f"Waiting {wait_time} seconds before retry...")

                time.sleep(wait_time)

            else:

                print(f"FAILED: {locality}. Moving to next locality.")

    return 0


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("\nURBANPROFIT - OPENSTREETMAP COLLECTION")
    print("Dataset:", OUTPUT_FILE)

    total_new_records = 0

    for index, place in enumerate(AREAS, start=1):

        print(
            f"\nLOCALITY {index}/{len(AREAS)}"
        )

        count = collect_locality(place)

        total_new_records += count

        # Allow the public Overpass service to recover.
        time.sleep(5)

    print("\n" + "=" * 60)
    print("COLLECTION PROCESS FINISHED")
    print("=" * 60)

    if os.path.exists(OUTPUT_FILE):

        final_data = pd.read_csv(OUTPUT_FILE)

        print("Total saved records:", len(final_data))
        print("\nCategory distribution:")

        print(
            final_data["business_category"].value_counts(
                dropna=False
            )
        )

        print("\nLocality distribution:")

        print(
            final_data["locality"].value_counts(
                dropna=False
            )
        )

        print("\nNew records extracted this run:", total_new_records)
        print("\nSaved file:", OUTPUT_FILE)

    else:

        print("No dataset was created. Check your internet connection.")


if __name__ == "__main__":
    main()
