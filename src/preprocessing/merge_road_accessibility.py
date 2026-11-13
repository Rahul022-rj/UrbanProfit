
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

MARKET_FILE = (
    BASE_DIR / "data" / "processed"
    / "urbanprofit_market_dataset_enriched.csv"
)

ROAD_FILE = (
    BASE_DIR / "data" / "processed"
    / "urbanprofit_road_accessibility.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "urbanprofit_market_dataset_final.csv"
)


def main():
    print("=" * 60)
    print("URBANPROFIT - MERGING ROAD ACCESSIBILITY DATA")
    print("=" * 60)

    # Load datasets
    market_df = pd.read_csv(MARKET_FILE)
    road_df = pd.read_csv(ROAD_FILE)

    print("\nMarket dataset:", market_df.shape)
    print("Road dataset:", road_df.shape)

    # Required columns
    required_road_columns = [
        "locality",
        "road_segment_count",
        "total_road_length_km",
        "intersection_count",
        "road_density_km_per_sq_km"
    ]

    missing_columns = [
        col for col in required_road_columns
        if col not in road_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing road columns: {missing_columns}"
        )

    if "locality" not in market_df.columns:
        raise ValueError("Market dataset has no locality column.")

    # Check duplicate locality records
    if market_df["locality"].duplicated().any():
        raise ValueError("Duplicate localities in market dataset.")

    if road_df["locality"].duplicated().any():
        raise ValueError("Duplicate localities in road dataset.")

    # Check missing values in road metrics
    if road_df[required_road_columns].isnull().any().any():
        raise ValueError("Missing values found in road dataset.")

    # Merge datasets
    final_df = market_df.merge(
        road_df[required_road_columns],
        on="locality",
        how="left",
        validate="one_to_one",
        indicator=True
    )

    # Verify every locality matched
    print("\nMerge results:")
    print(final_df["_merge"].value_counts())

    unmatched = final_df[
        final_df["_merge"] != "both"
    ]

    if not unmatched.empty:
        raise ValueError(
            "Some localities did not match:\n"
            + unmatched["locality"].to_string(index=False)
        )

    final_df.drop(columns=["_merge"], inplace=True)

    # Record data provenance and methodology
    final_df["road_data_source"] = "OpenStreetMap via OSMnx"
    final_df["road_network_type"] = "drive"
    final_df["road_study_radius_km"] = 3
    final_df["road_collection_date"] = "2026-11-11"

    # Save final dataset
    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\n" + "=" * 60)
    print("MERGE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("Total localities:", len(final_df))
    print("Total columns:", len(final_df.columns))
    print("Missing road density values:",
          final_df["road_density_km_per_sq_km"].isna().sum())

    print("\nRoad accessibility summary:")
    print(
        final_df[
            [
                "locality",
                "road_segment_count",
                "total_road_length_km",
                "intersection_count",
                "road_density_km_per_sq_km"
            ]
        ].to_string(index=False)
    )

    print("\nSaved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
