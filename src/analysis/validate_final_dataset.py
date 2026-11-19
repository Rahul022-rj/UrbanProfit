
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

FILE = (
    BASE_DIR / "data" / "processed"
    / "urbanprofit_market_dataset_final.csv"
)


def main():
    df = pd.read_csv(FILE)

    print("=" * 60)
    print("URBANPROFIT - FINAL DATASET VALIDATION")
    print("=" * 60)

    print("\n1. Dataset shape:", df.shape)

    print("\n2. Localities:")
    print(df["locality"].tolist())

    print("\n3. Duplicate rows:", df.duplicated().sum())
    print("Duplicate localities:", df["locality"].duplicated().sum())

    print("\n4. Missing values:")
    print(df.isnull().sum().to_string())

    print("\n5. Data types:")
    print(df.dtypes.to_string())

    print("\n6. Numerical summary:")
    print(df.select_dtypes(include="number").describe().round(2))

    print("\n7. Road density range:")
    print(
        df["road_density_km_per_sq_km"].min(),
        "to",
        df["road_density_km_per_sq_km"].max()
    )

    print("\n8. Population range:")
    print(df["population"].min(), "to", df["population"].max())

    print("\n9. Commercial rent range:")
    print(
        df["rent_per_sqft"].min()
        if "rent_per_sqft" in df.columns else "Not available"
    )

    print("\n10. Validation summary:")
    checks = {
        "Exactly 8 localities": len(df) == 8,
        "No duplicate localities": not df["locality"].duplicated().any(),
        "No duplicate rows": not df.duplicated().any(),
        "Road density complete": df["road_density_km_per_sq_km"].notna().all(),
        "Population complete": df["population"].notna().all(),
    }

    for check, passed in checks.items():
        print(f"{'PASS' if passed else 'CHECK'} - {check}")

    print("\nValidation completed.")


if __name__ == "__main__":
    main()
