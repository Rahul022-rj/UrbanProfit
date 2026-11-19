
import os
import time
import requests
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point, mapping

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

API_URL = "https://api.worldpop.org/v3/population"

YEAR = 2025
RADIUS_METRES = 3000

OUTPUT_DIR = "data/processed"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "urbanprofit_population_estimates.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Approximate locality centres: latitude, longitude
LOCALITY_CENTERS = {
    "Koramangala": (12.9352, 77.6245),
    "Electronic City": (12.8399, 77.6770),
    "Jayanagar": (12.9250, 77.5838),

    "HSR Layout": (12.9116225, 77.6388622),
    "Indiranagar": (12.97329, 77.64047),
    "Whitefield": (12.9700, 77.7150),
    "Marathahalli": (12.95363, 77.69759),
    "Malleshwaram": (13.00274, 77.57033)
}

# UTM Zone 43N is suitable for Bengaluru.
PROJECTED_CRS = "EPSG:32643"
GEOGRAPHIC_CRS = "EPSG:4326"


# --------------------------------------------------
# 2. CREATE 3 KM CIRCULAR STUDY AREA
# --------------------------------------------------

def create_study_area(latitude, longitude):

    point = Point(longitude, latitude)

    point_gdf = gpd.GeoDataFrame(
        {"name": ["study_centre"]},
        geometry=[point],
        crs=GEOGRAPHIC_CRS
    )

    projected = point_gdf.to_crs(PROJECTED_CRS)

    circle = projected.geometry.buffer(RADIUS_METRES)

    circle_gdf = gpd.GeoDataFrame(
        geometry=circle,
        crs=PROJECTED_CRS
    )

    circle_wgs84 = circle_gdf.to_crs(GEOGRAPHIC_CRS)

    return circle_wgs84.geometry.iloc[0]


# --------------------------------------------------
# 3. QUERY WORLDPOP API
# --------------------------------------------------

def get_population(geojson_geometry):

    payload = {
        "geojson": mapping(geojson_geometry),
        "year": YEAR
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# 4. COLLECT POPULATION FOR ALL LOCALITIES
# --------------------------------------------------

def main():

    results = []

    print("\nURBANPROFIT - WORLDPOP EXTRACTION")
    print("=" * 60)

    for index, (locality, coordinates) in enumerate(
        LOCALITY_CENTERS.items(),
        start=1
    ):

        latitude, longitude = coordinates

        print(f"\n[{index}/8] Processing: {locality}")
        print("Centre:", latitude, longitude)

        try:

            study_area = create_study_area(
                latitude,
                longitude
            )

            result = get_population(study_area)

            population = result.get("total_population")
            area = result.get("area_km2")
            density = result.get("population_density")

            if population is None:
                raise ValueError(
                    f"Population missing in API response: {result}"
                )

            record = {
                "locality": locality,
                "latitude": latitude,
                "longitude": longitude,
                "study_radius_km": RADIUS_METRES / 1000,
                "population": population,
                "area_sq_km": area,
                "population_density": density,
                "population_year": result.get("data_year", YEAR),
                "population_source": result.get(
                    "data_source",
                    "WorldPop Global2 R2025A, 100 m"
                ),
                "source_doi": "10.5258/SOTON/WP00839",
                "method": "3 km radius circular study area"
            }

            results.append(record)

            print("Population:", round(population))
            print("Area (km²):", area)
            print("Density:", round(density, 2))

        except Exception as error:

            print("ERROR:", locality, "-", error)

        time.sleep(1)

    # --------------------------------------------------
    # 5. SAVE RESULTS
    # --------------------------------------------------

    if results:

        df = pd.DataFrame(results)

        df.to_csv(OUTPUT_FILE, index=False)

        print("\n" + "=" * 60)
        print("POPULATION EXTRACTION COMPLETED")
        print("=" * 60)

        print("\nResults:")
        print(
            df[
                [
                    "locality",
                    "population",
                    "area_sq_km",
                    "population_density"
                ]
            ].to_string(index=False)
        )

        print("\nSuccessful localities:", len(df), "/ 8")
        print("Saved:", OUTPUT_FILE)

    else:

        print("\nNo population results were collected.")


if __name__ == "__main__":
    main()
