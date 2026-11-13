
import os
import time
import warnings

import osmnx as ox
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

OUTPUT_DIR = "data/processed"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "urbanprofit_road_accessibility.csv"
)

RADIUS_METRES = 3000

PROJECTED_CRS = "EPSG:32643"
GEOGRAPHIC_CRS = "EPSG:4326"

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

os.makedirs(OUTPUT_DIR, exist_ok=True)

# OSMnx settings
ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.timeout = 180
ox.settings.requests_timeout = 180

# --------------------------------------------------
# 2. CREATE STUDY AREA
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

    return circle_gdf.geometry.iloc[0]


# --------------------------------------------------
# 3. COLLECT ROAD NETWORK
# --------------------------------------------------

def collect_road_data(locality, coordinates):

    latitude, longitude = coordinates

    print("\nProcessing:", locality)

    study_area = create_study_area(
        latitude,
        longitude
    )

    # Convert study area to WGS84 for OSMnx.
    area_gdf = gpd.GeoDataFrame(
        geometry=[study_area],
        crs=PROJECTED_CRS
    ).to_crs(GEOGRAPHIC_CRS)

    polygon = area_gdf.geometry.iloc[0]

    print("Downloading driving road network...")

    graph = ox.graph_from_polygon(
        polygon,
        network_type="drive",
        simplify=True,
        retain_all=True,
        truncate_by_edge=True
    )

    if graph.number_of_nodes() == 0:
        raise ValueError("No road-network nodes returned.")

    if graph.number_of_edges() == 0:
        raise ValueError("No road-network edges returned.")

    # Convert to an undirected graph so reciprocal
    # two-way road edges are not counted twice.
    try:
        undirected_graph = ox.convert.to_undirected(graph)
    except AttributeError:
        undirected_graph = ox.utils_graph.get_undirected(graph)

    # Convert network data into GeoDataFrames.
    nodes, edges = ox.graph_to_gdfs(
        undirected_graph,
        nodes=True,
        edges=True,
        fill_edge_geometry=True
    )

    # Project to metres for accurate length calculations.
    nodes = nodes.to_crs(PROJECTED_CRS)
    edges = edges.to_crs(PROJECTED_CRS)

    # --------------------------------------------------
    # 4. CLIP ROAD SEGMENTS TO STUDY AREA
    # --------------------------------------------------

    clipped_lengths = []

    for geometry in edges.geometry:

        if geometry is None or geometry.is_empty:
            continue

        clipped = geometry.intersection(study_area)

        if clipped.is_empty:
            continue

        length = clipped.length

        if length > 0:
            clipped_lengths.append(length)

    total_road_length_km = (
        sum(clipped_lengths) / 1000
    )

    road_segment_count = len(clipped_lengths)

    # --------------------------------------------------
    # 5. COUNT ROAD INTERSECTIONS
    # --------------------------------------------------

    # Count network nodes inside the study area
    # that connect to at least three road segments.
    intersection_count = 0

    for node_id, node in nodes.iterrows():

        if not study_area.covers(node.geometry):
            continue

        degree = undirected_graph.degree(node_id)

        if degree >= 3:
            intersection_count += 1

    # --------------------------------------------------
    # 6. CALCULATE ROAD DENSITY
    # --------------------------------------------------

    area_sq_km = study_area.area / 1_000_000

    road_density = (
        total_road_length_km / area_sq_km
        if area_sq_km > 0
        else 0
    )

    print("Road segments:", road_segment_count)
    print("Road length (km):", round(total_road_length_km, 2))
    print("Intersections:", intersection_count)
    print("Road density:", round(road_density, 2))

    return {
        "locality": locality,
        "latitude": latitude,
        "longitude": longitude,
        "study_radius_km": RADIUS_METRES / 1000,
        "area_sq_km": area_sq_km,
        "road_segment_count": road_segment_count,
        "total_road_length_km": total_road_length_km,
        "intersection_count": intersection_count,
        "road_density_km_per_sq_km": road_density,
        "network_type": "drive",
        "source": "OpenStreetMap",
        "method": "OSMnx driving network within 3 km circular study area"
    }


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    results = []

    # Load previously collected records.
    if os.path.exists(OUTPUT_FILE):
        existing = pd.read_csv(OUTPUT_FILE)

        results = existing.to_dict("records")

        print(
            "Previously collected localities:",
            existing["locality"].tolist()
        )

    completed = {
        row["locality"] for row in results
    }

    print("\nURBANPROFIT - ROAD ACCESSIBILITY RETRY")
    print("=" * 60)

    for locality, coordinates in LOCALITY_CENTERS.items():

        if locality in completed:
            print("\nSkipping already collected:", locality)
            continue

        print("\nCollecting:", locality)

        success = False

        for attempt in range(1, 4):

            try:

                print(f"Attempt {attempt}/3")

                result = collect_road_data(
                    locality,
                    coordinates
                )

                results.append(result)

                # Save after every successful locality.
                pd.DataFrame(results).to_csv(
                    OUTPUT_FILE,
                    index=False
                )

                success = True

                print("SUCCESS:", locality)
                break

            except Exception as error:

                print("ERROR:", error)

                if attempt < 3:
                    wait_time = 30 * (2 ** (attempt - 1))

                    print(
                        f"Retrying after {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

        if not success:
            print("FAILED AFTER 3 ATTEMPTS:", locality)

        time.sleep(15)

    # Final report
    final_df = pd.DataFrame(results)

    print("\n" + "=" * 60)
    print("ROAD ACCESSIBILITY RETRY COMPLETED")
    print("=" * 60)

    if not final_df.empty:

        print(
            final_df[
                [
                    "locality",
                    "road_segment_count",
                    "total_road_length_km",
                    "intersection_count",
                    "road_density_km_per_sq_km"
                ]
            ].round(2).to_string(index=False)
        )

    print(
        "\nCollected localities:",
        final_df["locality"].nunique(),
        "/ 8"
    )

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
