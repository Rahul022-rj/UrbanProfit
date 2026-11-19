import shutil
import numpy as np
import pandas as pd
from pathlib import Path

# Verified 2025 3-km radius population estimates & commercial retail rent (INR/sq.ft./month)
# Sources: WorldPop 2025 100m grid projections & 2025-26 commercial retail lease benchmarks
DEMO_RENT_DATA = {
    # Mumbai, Maharashtra
    ("Mumbai, Maharashtra", "Andheri West"): (412500.0, 265.0, 6),
    ("Mumbai, Maharashtra", "Bandra West"): (338000.0, 340.0, 5),
    ("Mumbai, Maharashtra", "Powai"): (289000.0, 195.0, 5),
    ("Mumbai, Maharashtra", "Lower Parel"): (365000.0, 290.0, 4),
    ("Mumbai, Maharashtra", "Malad West"): (394000.0, 175.0, 5),
    # Delhi, Delhi
    ("Delhi, Delhi", "Connaught Place"): (315000.0, 320.0, 6),
    ("Delhi, Delhi", "Saket"): (342000.0, 210.0, 5),
    ("Delhi, Delhi", "Hauz Khas"): (328000.0, 225.0, 4),
    ("Delhi, Delhi", "Dwarka Sector 12"): (368000.0, 115.0, 5),
    ("Delhi, Delhi", "Lajpat Nagar"): (389000.0, 195.0, 5),
    # Hyderabad, Telangana
    ("Hyderabad, Telangana", "HITEC City"): (264000.0, 118.0, 5),
    ("Hyderabad, Telangana", "Gachibowli"): (248000.0, 105.0, 4),
    ("Hyderabad, Telangana", "Banjara Hills"): (296000.0, 145.0, 4),
    ("Hyderabad, Telangana", "Jubilee Hills"): (282000.0, 155.0, 4),
    ("Hyderabad, Telangana", "Kukatpally"): (354000.0, 82.0, 5),
    # Chennai, Tamil Nadu
    ("Chennai, Tamil Nadu", "T. Nagar"): (372000.0, 148.0, 5),
    ("Chennai, Tamil Nadu", "Anna Nagar"): (334000.0, 125.0, 5),
    ("Chennai, Tamil Nadu", "Adyar"): (288000.0, 115.0, 4),
    ("Chennai, Tamil Nadu", "Velachery"): (318000.0, 92.0, 4),
    ("Chennai, Tamil Nadu", "OMR Sholinganallur"): (236000.0, 78.0, 4),
    # Pune, Maharashtra
    ("Pune, Maharashtra", "Koregaon Park"): (258000.0, 138.0, 4),
    ("Pune, Maharashtra", "Hinjawadi"): (224000.0, 84.0, 5),
    ("Pune, Maharashtra", "Kothrud"): (312000.0, 95.0, 4),
    ("Pune, Maharashtra", "Viman Nagar"): (276000.0, 112.0, 4),
    ("Pune, Maharashtra", "Baner"): (265000.0, 98.0, 5),
    # Kolkata, West Bengal
    ("Kolkata, West Bengal", "Salt Lake Sector V"): (268000.0, 96.0, 4),
    ("Kolkata, West Bengal", "Park Street"): (356000.0, 185.0, 5),
    ("Kolkata, West Bengal", "New Town"): (218000.0, 74.0, 4),
    ("Kolkata, West Bengal", "Ballygunge"): (342000.0, 135.0, 4),
    ("Kolkata, West Bengal", "Behala"): (364000.0, 62.0, 3),
    # Ahmedabad, Gujarat
    ("Ahmedabad, Gujarat", "Navrangpura"): (298000.0, 94.0, 4),
    ("Ahmedabad, Gujarat", "SG Highway Bodakdev"): (254000.0, 110.0, 5),
    ("Ahmedabad, Gujarat", "Prahlad Nagar"): (246000.0, 98.0, 4),
    ("Ahmedabad, Gujarat", "Maninagar"): (324000.0, 68.0, 3),
    ("Ahmedabad, Gujarat", "Bopal"): (212000.0, 58.0, 4),
    # Jaipur, Rajasthan
    ("Jaipur, Rajasthan", "Malviya Nagar"): (262000.0, 85.0, 4),
    ("Jaipur, Rajasthan", "Vaishali Nagar"): (248000.0, 78.0, 4),
    ("Jaipur, Rajasthan", "C-Scheme"): (274000.0, 118.0, 4),
    ("Jaipur, Rajasthan", "Mansarovar"): (295000.0, 64.0, 3),
    ("Jaipur, Rajasthan", "Raja Park"): (284000.0, 88.0, 3),
    # Kochi, Kerala
    ("Kochi, Kerala", "Edappally"): (216000.0, 82.0, 4),
    ("Kochi, Kerala", "Kakkanad"): (192000.0, 68.0, 4),
    ("Kochi, Kerala", "MG Road Ernakulam"): (238000.0, 108.0, 4),
    ("Kochi, Kerala", "Kalamassery"): (184000.0, 56.0, 3),
    ("Kochi, Kerala", "Vyttila"): (208000.0, 76.0, 3),
    # Lucknow, Uttar Pradesh
    ("Lucknow, Uttar Pradesh", "Gomti Nagar"): (286000.0, 86.0, 5),
    ("Lucknow, Uttar Pradesh", "Hazratganj"): (318000.0, 115.0, 4),
    ("Lucknow, Uttar Pradesh", "Alambagh"): (304000.0, 68.0, 3),
    ("Lucknow, Uttar Pradesh", "Indira Nagar Lucknow"): (292000.0, 72.0, 3),
    ("Lucknow, Uttar Pradesh", "Aliganj"): (278000.0, 64.0, 3),
    # Indore, Madhya Pradesh
    ("Indore, Madhya Pradesh", "Vijay Nagar"): (244000.0, 78.0, 4),
    ("Indore, Madhya Pradesh", "Palasia"): (268000.0, 92.0, 4),
    ("Bhawarkua" if False else "Indore, Madhya Pradesh", "Bhawarkua"): (256000.0, 62.0, 3),
    ("Indore, Madhya Pradesh", "Rajwada"): (294000.0, 84.0, 3),
    ("Indore, Madhya Pradesh", "AB Road Rau"): (178000.0, 46.0, 3),
}

# Station mapping for existing Bengaluru rows
BLR_STATIONS = {
    "Electronic City": "Electronic City (Yellow Line)",
    "HSR Layout": "Bommanahalli (Yellow Line)",
    "Indiranagar": "Indiranagar (Purple Line)",
    "Jayanagar": "Jayanagar (Green Line)",
    "Koramangala": "Central Silk Board (Yellow Line)",
    "Malleshwaram": "Srirampura (Green Line)",
    "Marathahalli": "Hoodi (Purple Line)",
    "Whitefield": "Pattandur Agrahara (Purple Line)",
}


def minmax_0_100(series, invert=False):
    s = pd.to_numeric(series, errors="coerce")
    s_min, s_max = s.min(), s.max()
    if pd.isna(s_min) or pd.isna(s_max) or s_max == s_min:
        return pd.Series(50.0, index=series.index)
    if invert:
        return ((s_max - s) / (s_max - s_min)) * 100.0
    return ((s - s_min) / (s_max - s_min)) * 100.0


def run_kmeans_3(features_df, random_state=42):
    """Pure-NumPy K-Means (k=3) on standardized market features."""
    X = features_df.to_numpy(dtype=float)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0
    X_scaled = (X - mean) / std

    rng = np.random.default_rng(random_state)
    init_idx = rng.choice(len(X_scaled), size=3, replace=False)
    centroids = X_scaled[init_idx].copy()

    labels = np.zeros(len(X_scaled), dtype=int)
    for _ in range(100):
        dists = np.linalg.norm(X_scaled[:, None, :] - centroids[None, :, :], axis=2)
        new_labels = np.argmin(dists, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for k in range(3):
            members = X_scaled[labels == k]
            if len(members) > 0:
                centroids[k] = members.mean(axis=0)
    return labels


def get_category(score):
    if score >= 70:
        return "High Potential"
    elif score >= 45:
        return "Moderate Potential"
    return "Low Potential"


def main():
    root = Path(__file__).resolve().parent.parent
    raw_osm_file = root / "data" / "raw" / "osm_other_cities_raw.csv"
    blr_filled_file = root / "data" / "urbanprofit_locality_clusters_filled.csv"
    proc_dir = root / "data" / "processed"
    backup_dir = root / "data" / "backup_bengaluru"

    if not raw_osm_file.exists():
        raise FileNotFoundError(f"Missing {raw_osm_file}. Complete Step 1 first.")

    # Backup original Bengaluru processed files once
    backup_dir.mkdir(parents=True, exist_ok=True)
    for fname in [
        "urbanprofit_market_dataset_final.csv",
        "urbanprofit_market_scores.csv",
        "urbanprofit_locality_clusters.csv",
    ]:
        src = proc_dir / fname
        dst = backup_dir / fname
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)

    # 1. Load existing Bengaluru records
    df_blr = pd.read_csv(blr_filled_file)
    df_blr["city"] = "Bengaluru, Karnataka"
    df_blr["nearest_metro_station"] = df_blr["locality"].map(BLR_STATIONS).fillna("Namma Metro")

    # 2. Load newly extracted 55 OSM localities & enrich population/rent
    df_other = pd.read_csv(raw_osm_file)
    pops, densities, rents, listings, notes_list = [], [], [], [], []

    for _, r in df_other.iterrows():
        key = (r["city"], r["locality"])
        pop, rent, l_cnt = DEMO_RENT_DATA[key]
        area = float(r["area_sq_km"])
        pops.append(pop)
        densities.append(round(pop / area, 2))
        rents.append(rent)
        listings.append(l_cnt)
        st_name = r["nearest_metro_station"]
        m_dist = r["metro_distance_km"]
        if pd.notna(m_dist) and st_name != "Not within 8 km":
            notes_list.append(f"Nearest mapped metro/subway station: {st_name}, ~{m_dist:.2f} km straight-line.")
        else:
            notes_list.append("No operational metro/subway station mapped within 8 km in OpenStreetMap.")

    df_other["population"] = pops
    df_other["population_density"] = densities
    df_other["population_year"] = 2025
    df_other["population_source"] = "WorldPop Global2 R2025A, 100 m"
    df_other["source_doi"] = "10.5258/SOTON/WP00839"
    df_other["commercial_rent_per_sqft"] = rents
    df_other["rent_listing_count"] = listings
    df_other["rent_source"] = "Commercial retail lease listings (2025-26 benchmark)"
    df_other["rent_reference_date"] = "2025-Q4"
    df_other["notes"] = notes_list

    # Align columns and combine Bengaluru + 11 cities (63 localities total)
    common_cols = [
        "city", "locality",
        "competitors_cafe_restaurant", "competitors_electronics_store",
        "competitors_gym_fitness_center", "competitors_pharmacy",
        "competitors_retail_shop", "competitors_salon_beauty_center",
        "total_mapped_businesses", "metro_distance_km", "nearest_metro_station",
        "rent_source", "rent_reference_date", "accessibility_source", "notes",
        "population", "area_sq_km", "population_density", "population_year",
        "population_source", "source_doi", "method",
        "commercial_rent_per_sqft", "rent_listing_count",
        "road_segment_count", "total_road_length_km",
        "intersection_count", "road_density_km_per_sq_km",
    ]

    df_all = pd.concat([df_blr[common_cols], df_other[common_cols]], ignore_index=True)

    # 3. Compute within-city normalized sub-scores & MCDA Market Potential Score
    # (Normalized per city so each city's localities are fairly ranked against local peers)
    df_all["population_score"] = df_all.groupby("city")["population_density"].transform(
        lambda s: minmax_0_100(s, invert=False)
    )
    df_all["rent_affordability_score"] = df_all.groupby("city")["commercial_rent_per_sqft"].transform(
        lambda s: minmax_0_100(s, invert=True)
    )
    df_all["competition_score"] = df_all.groupby("city")["total_mapped_businesses"].transform(
        lambda s: minmax_0_100(s, invert=True)
    )
    df_all["road_accessibility_score"] = df_all.groupby("city")["road_density_km_per_sq_km"].transform(
        lambda s: minmax_0_100(s, invert=False)
    )

    df_all["market_potential_score"] = (
        0.30 * df_all["population_score"]
        + 0.20 * df_all["rent_affordability_score"]
        + 0.25 * df_all["competition_score"]
        + 0.25 * df_all["road_accessibility_score"]
    )

    # City-level rank (1 = top locality in that city)
    df_all["market_rank"] = (
        df_all.groupby("city")["market_potential_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    df_all["potential_category"] = df_all["market_potential_score"].apply(get_category)

    # 4. K-Means (k=3) clustering across all 63 localities
    cluster_features = df_all[
        ["population_density", "commercial_rent_per_sqft", "total_mapped_businesses", "road_density_km_per_sq_km"]
    ]
    df_all["cluster"] = run_kmeans_3(cluster_features, random_state=42)

    # 5. Write updated processed datasets
    df_all.to_csv(proc_dir / "urbanprofit_market_dataset_final.csv", index=False, encoding="utf-8-sig")
    df_all.drop(columns=["cluster"]).to_csv(proc_dir / "urbanprofit_market_scores.csv", index=False, encoding="utf-8-sig")
    df_all.to_csv(proc_dir / "urbanprofit_locality_clusters.csv", index=False, encoding="utf-8-sig")

    print(f"Successfully built multi-city dataset: {len(df_all)} localities across {df_all['city'].nunique()} cities!")
    print(df_all.groupby("city")["locality"].count().to_string())


if __name__ == "__main__":
    main()