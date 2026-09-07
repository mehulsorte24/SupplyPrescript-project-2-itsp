import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path.cwd()

RISK_FEATURES = {
    "supplier_risk": "Low supplier reliability",
    "weather_risk": "Severe weather conditions",
    "traffic_risk": "High traffic conditions",
    "inventory_risk": "Low inventory level",
    "warehouse_risk": "High warehouse load",
    "distance_risk": "Long transportation distance",
    "transport_risk": "Higher transport disruption risk",
    "priority_risk": "High shipment priority",
    "fuel_pressure": "High fuel price pressure",
    "lead_time_pressure": "Long lead time",
}


def calculate_driver_score(row, feature):
    value = row.get(feature, 0)

    if pd.isna(value):
        return 0.0

    return max(float(value), 0.0)


def get_risk_drivers(row, top_n=4):
    drivers = []

    for feature, description in RISK_FEATURES.items():
        if feature not in row.index:
            continue

        score = calculate_driver_score(row, feature)

        if score > 0:
            drivers.append(
                {
                    "feature": feature,
                    "description": description,
                    "score": score,
                }
            )

    drivers.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return drivers[:top_n]


def generate_explanation(row, top_n=4):
    drivers = get_risk_drivers(row, top_n)

    return [
        driver["description"]
        for driver in drivers
    ]


def explain_dataset(input_file, limit=10, top_n=4):
    df = pd.read_csv(input_file)

    if df.empty:
        raise ValueError(
            "Input dataset contains no records."
        )

    sample = df.head(limit).copy()

    sample["risk_drivers"] = sample.apply(
        lambda row: generate_explanation(
            row,
            top_n
        ),
        axis=1
    )

    return sample


def print_explainability_report(df):
    print()
    print("RISK DRIVER / EXPLAINABILITY ANALYSIS")
    print("=" * 100)

    for _, row in df.iterrows():
        shipment_id = row.get(
            "shipment_id",
            "UNKNOWN"
        )

        risk_score = row.get(
            "overall_risk_score",
            0
        )

        print()
        print(f"Shipment: {shipment_id}")
        print(
            f"Overall Risk Score: "
            f"{float(risk_score):.2f}"
        )

        print("Top Risk Drivers:")

        drivers = row.get(
            "risk_drivers",
            []
        )

        if not drivers:
            print(
                "  - No significant risk drivers detected."
            )
            continue

        for index, driver in enumerate(
            drivers,
            start=1
        ):
            print(
                f"  {index}. {driver}"
            )

    print()
    print("=" * 100)

    total_shipments = len(df)

    driver_counts = {}

    for drivers in df["risk_drivers"]:
        for driver in drivers:
            driver_counts[driver] = (
                driver_counts.get(
                    driver,
                    0
                ) + 1
            )

    print("RISK DRIVER FREQUENCY")
    print("=" * 100)

    if driver_counts:
        sorted_drivers = sorted(
            driver_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )

        for driver, count in sorted_drivers:
            percentage = (
                count / total_shipments
            ) * 100

            print(
                f"{driver:<40} "
                f"{count:>3} shipments "
                f"({percentage:.1f}%)"
            )
    else:
        print(
            "No risk drivers detected."
        )

    print()
    print("=" * 100)


def main():
    print("=" * 100)
    print("SUPPLY PRESCRIPT - RISK DRIVER ENGINE")
    print("=" * 100)

    input_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "ml_features.csv"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {input_file}"
        )

    explained_data = explain_dataset(
        str(input_file),
        limit=10,
        top_n=4
    )

    print_explainability_report(
        explained_data
    )

    print()
    print("=" * 100)
    print("RISK DRIVER ENGINE COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()
