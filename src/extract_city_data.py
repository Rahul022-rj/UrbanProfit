import time
import math
import requests
import pandas as pd
from pathlib import Path

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

HEADERS = {
    "User-Agent": "UrbanProfit-MCA-Project/1.0 (Academic Research)"
}

CITY_LOCALITIES = {
    "Mumbai, Maharashtra": [
        ("Andheri West", 19.1364, 72.8296),
        ("Bandra West", 19.0596, 72.8295),
        ("Powai", 19.1176, 72.9060),
        ("Lower Parel", 18.9982, 72.8301),
        ("Malad West", 19.1874, 72.8484),
    ],
    "Delhi, Delhi": [
        ("Connaught Place", 28.6315, 77.2167),
        ("Saket", 28.5244, 77.2066),
        ("Hauz Khas", 28.5494, 77.2001),
        ("Dwarka Sector 12", 28.5921, 77.0460),
        ("Lajpat Nagar", 28.5677, 77.2433),
    ],
    "Hyderabad, Telangana": [
        ("HITEC City", 17.4435, 78.3772),
        ("Gachibowli", 17.4401, 78.3489),
        ("Banjara Hills", 17.4126, 78.4392),
        ("Jubilee Hills", 17.4326, 78.4071),
        ("Kukatpally", 17.4948, 78.3996),
    ],
    "Chennai, Tamil Nadu": [
        ("T. Nagar", 13.0418, 80.2341),
        ("Anna Nagar", 13.0850, 80.2101),
        ("Adyar", 13.0012, 80.2565),
        ("Velachery", 12.9815, 80.2180),
        ("OMR Sholinganallur", 12.9010, 80.2279),
    ],
    "Pune, Maharashtra": [
        ("Koregaon Park", 18.5362, 73.8940),
        ("Hinjawadi", 18.5913, 73.7389),
        ("Kothrud", 18.5074, 73.8077),
        ("Viman Nagar", 18.5679, 73.9143),
        ("Baner", 18.5590, 73.7868),
    ],
    "Kolkata, West Bengal": [
        ("Salt Lake Sector V", 22.5735, 88.4331),
        ("Park Street", 22.5535, 88.3525),
        ("New Town", 22.5922, 88.4847),
        ("Ballygunge", 22.5280, 88.3659),
        ("Behala", 22.4981, 88.3108),
    ],
    "Ahmedabad, Gujarat": [
        ("Navrangpura", 23.0365, 72.5611),
        ("SG Highway Bodakdev", 23.0387, 72.5117),
        ("Prahlad Nagar", 23.0120, 72.5108),
        ("Maninagar", 22.9962, 72.6032),
        ("Bopal", 23.0337, 72.4634),
    ],
    "Jaipur, Rajasthan": [
        ("Malviya Nagar", 26.8549, 75.8243),
        ("Vaishali Nagar", 26.9114, 75.7445),
        ("C-Scheme", 26.9075, 75.7995),
        ("Mansarovar", 26.8682, 75.7647),
        ("Raja Park", 26.8965, 75.8295),
    ],
    "Kochi, Kerala": [
        ("Edappally", 10.0261, 76.3125),
        ("Kakkanad", 10.0159, 76.3419),
        ("MG Road Ernakulam", 9.9772, 76.2830),
        ("Kalamassery", 10.0531, 76.3528),
        ("Vyttila", 9.9679, 76.3183),
    ],
    "Lucknow, Uttar Pradesh": [
        ("Gomti Nagar", 26.8467, 80.9462),
        ("Hazratganj", 26.8489, 80.9425),
        ("Alambagh", 26.8130, 80.9038),
        ("Indira Nagar Lucknow", 26.8825, 80.9961),
        ("Aliganj", 26.8961, 80.9436),
    ],
    "Indore, Madhya Pradesh": [
        ("Vijay Nagar", 22.7533, 75.8937),
        ("Palasia", 22.7244, 75.8839),
        ("Bhawarkua", 22.6927, 75.8676),
        ("Rajwada", 22.7186, 75.8557),
        ("AB Road Rau", 22.6391, 75.8147),
    ],
}

RADIUS_M = 3000
STUDY_AREA_SQ_KM = round(math.pi * (3.0 ** 2), 4)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def query_overpass(ql_query):
    for attempt in range(5):
        for url in OVERPASS_URLS:
            try:
                resp = requests.post(url, data={"data": ql_query}, headers=HEADERS, timeout=75)
                if resp.status_code == 200:
                    return resp.json()
                print(f"  [HTTP {resp.status_code}] Switching mirror...")
            except Exception as e:
                print(f"  [Retry] {url} -> {type(e).__name__}")
            time.sleep(2)
        time.sleep(5)
    raise RuntimeError("Overpass API timed out. Re-run script to resume from last saved locality.")


def fetch_locality_osm_metrics(city, locality, lat, lon):
    print(f"Extracting real OSM data for: {locality} ({city})...")

    # Query 1: Nodes + Ways only (`nw` avoids heavy relation/multipolygon timeouts)
    ql_pois = f"""
    [out:json][timeout:60];
    (
      nw(around:{RADIUS_M},{lat},{lon})["amenity"~"^(cafe|restaurant|fast_food|pharmacy)$"];
      nw(around:{RADIUS_M},{lat},{lon})["shop"~"^(electronics|mobile_phone|supermarket|convenience|clothes|department_store|mall|hairdresser|beauty)$"];
      nw(around:{RADIUS_M},{lat},{lon})["leisure"="fitness_centre"];
      node(around:8000,{lat},{lon})["station"="subway"];
      node(around:8000,{lat},{lon})["railway"="station"]["subway"="yes"];
    );
    out center tags;
    """

    # Query 2: Road network geometry
    ql_roads = f"""
    [out:json][timeout:60];
    way(around:{RADIUS_M},{lat},{lon})["highway"~"^(trunk|primary|secondary|tertiary|unclassified|residential)$"];
    out geom tags;
    """

    poi_data = query_overpass(ql_pois)
    time.sleep(1.5)
    road_data = query_overpass(ql_roads)
    counts = {
        "competitors_cafe_restaurant": 0,
        "competitors_electronics_store": 0,
        "competitors_gym_fitness_center": 0,
        "competitors_pharmacy": 0,
        "competitors_retail_shop": 0,
        "competitors_salon_beauty_center": 0,
    }

    nearest_station_name = "Not within 8 km"
    min_metro_dist = None

    for el in poi_data.get("elements", []):
        tags = el.get("tags", {})
        if el["type"] == "node" and (tags.get("station") == "subway" or tags.get("subway") == "yes"):
            d = haversine_km(lat, lon, el["lat"], el["lon"])
            if min_metro_dist is None or d < min_metro_dist:
                min_metro_dist = d
                nearest_station_name = tags.get("name", "Metro Station")
            continue

        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        leisure = tags.get("leisure", "")

        if amenity in ("cafe", "restaurant", "fast_food"):
            counts["competitors_cafe_restaurant"] += 1
        elif amenity == "pharmacy":
            counts["competitors_pharmacy"] += 1
        elif leisure == "fitness_centre":
            counts["competitors_gym_fitness_center"] += 1
        elif shop in ("electronics", "mobile_phone"):
            counts["competitors_electronics_store"] += 1
        elif shop in ("hairdresser", "beauty"):
            counts["competitors_salon_beauty_center"] += 1
        elif shop in ("supermarket", "convenience", "clothes", "department_store", "mall"):
            counts["competitors_retail_shop"] += 1

    road_segment_count = 0
    total_road_length_km = 0.0
    coord_degree = {}

    for el in road_data.get("elements", []):
        geom = el.get("geometry", [])
        if len(geom) >= 2:
            road_segment_count += 1
            for idx in range(len(geom) - 1):
                p1, p2 = geom[idx], geom[idx + 1]
                total_road_length_km += haversine_km(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
            for pt in geom:
                key = (round(pt["lat"], 6), round(pt["lon"], 6))
                coord_degree[key] = coord_degree.get(key, 0) + 1

    intersection_count = sum(1 for deg in coord_degree.values() if deg >= 3)
    road_density = round(total_road_length_km / STUDY_AREA_SQ_KM, 6)
    total_businesses = sum(counts.values())

    return {
        "city": city,
        "locality": locality,
        "latitude": lat,
        "longitude": lon,
        **counts,
        "total_mapped_businesses": total_businesses,
        "metro_distance_km": round(min_metro_dist, 2) if min_metro_dist is not None else None,
        "nearest_metro_station": nearest_station_name,
        "area_sq_km": STUDY_AREA_SQ_KM,
        "road_segment_count": road_segment_count,
        "total_road_length_km": round(total_road_length_km, 6),
        "intersection_count": intersection_count,
        "road_density_km_per_sq_km": road_density,
        "accessibility_source": "OpenStreetMap Overpass API (3 km radius study area)",
        "method": "3 km radius circular study area",
    }


def main():
    out_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "osm_other_cities_raw.csv"

    existing_rows = []
    done_pairs = set()
    if out_file.exists():
        df_existing = pd.read_csv(out_file)
        existing_rows = df_existing.to_dict("records")
        done_pairs = set(zip(df_existing["city"], df_existing["locality"]))
        print(f"Resuming: {len(done_pairs)} localities already extracted.")

    rows = list(existing_rows)
    for city, locs in CITY_LOCALITIES.items():
        for locality, lat, lon in locs:
            if (city, locality) in done_pairs:
                continue
            row = fetch_locality_osm_metrics(city, locality, lat, lon)
            rows.append(row)
            pd.DataFrame(rows).to_csv(out_file, index=False, encoding="utf-8-sig")
            time.sleep(3)

    print(f"\nDone! Total {len(rows)} real-world locality records saved to: {out_file}")


if __name__ == "__main__":
    main()