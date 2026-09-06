from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# RISK MAPPINGS
# ============================================================

WEATHER_RISK = {
    "Low": 0.0,
    "Medium": 0.33,
    "High": 0.67,
    "Severe": 1.0
}

TRAFFIC_RISK = {
    "Low": 0.0,
    "Medium": 0.5,
    "High": 1.0
}

TRANSPORT_RISK = {
    "Air": 0.10,
    "Rail": 0.40,
    "Road": 0.50,
    "Sea": 0.80
}

PRIORITY_RISK = {
    "Low": 0.0,
    "Medium": 0.33,
    "High": 0.67,
    "Critical": 1.0
}


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create predictive risk features from shipment data.

    The original shipment columns are preserved and additional
    machine-learning features are added.
    """

    features = df.copy()

    # --------------------------------------------------------
    # Supplier risk
    # --------------------------------------------------------

    features["supplier_risk"] = (
        1 - features["supplier_reliability"]
    )

    # --------------------------------------------------------
    # Weather risk
    # --------------------------------------------------------

    features["weather_risk"] = (
        features["weather_severity"]
        .map(WEATHER_RISK)
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Traffic risk
    # --------------------------------------------------------

    features["traffic_risk"] = (
        features["traffic_level"]
        .map(TRAFFIC_RISK)
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Inventory risk
    #
    # Lower inventory means greater operational risk.
    # Inventory is normalized between 0 and 100.
    # --------------------------------------------------------

    features["inventory_risk"] = (
        1 - (
            features["inventory_level"] / 100
        )
    ).clip(0, 1)

    # --------------------------------------------------------
    # Warehouse congestion risk
    # --------------------------------------------------------

    features["warehouse_risk"] = (
        features["warehouse_load"]
        .clip(0, 1)
    )

    # --------------------------------------------------------
    # Distance risk
    #
    # 3000 km is treated as the upper reference point
    # because the simulator generates distances up to 3000 km.
    # --------------------------------------------------------

    features["distance_risk"] = (
        features["distance_km"] / 3000
    ).clip(0, 1)

    # --------------------------------------------------------
    # Transport risk
    # --------------------------------------------------------

    features["transport_risk"] = (
        features["transport_mode"]
        .map(TRANSPORT_RISK)
        .fillna(0.5)
    )

    # --------------------------------------------------------
    # Priority risk
    # --------------------------------------------------------

    features["priority_risk"] = (
        features["priority"]
        .map(PRIORITY_RISK)
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Fuel price pressure
    #
    # Simulator range is approximately 90–150.
    # Normalize this into a 0–1 scale.
    # --------------------------------------------------------

    fuel_min = 90
    fuel_max = 150

    features["fuel_pressure"] = (
        (
            features["fuel_price_index"] - fuel_min
        )
        / (fuel_max - fuel_min)
    ).clip(0, 1)

    # --------------------------------------------------------
    # Lead-time pressure
    #
    # Longer planned lead time represents greater exposure
    # to operational disruption.
    # --------------------------------------------------------

    features["lead_time_pressure"] = (
        features["lead_time_days"] / 20
    ).clip(0, 1)

    # --------------------------------------------------------
    # Combined operational risk score
    #
    # Weighted score designed as a transparent feature rather
    # than replacing the machine-learning model.
    # --------------------------------------------------------

    features["overall_risk_score"] = (
        features["supplier_risk"] * 0.20
        + features["weather_risk"] * 0.15
        + features["traffic_risk"] * 0.10
        + features["inventory_risk"] * 0.15
        + features["warehouse_risk"] * 0.10
        + features["distance_risk"] * 0.10
        + features["transport_risk"] * 0.05
        + features["priority_risk"] * 0.05
        + features["fuel_pressure"] * 0.05
        + features["lead_time_pressure"] * 0.05
    )

    # --------------------------------------------------------
    # Risk category
    # --------------------------------------------------------

    features["risk_category"] = pd.cut(
        features["overall_risk_score"],
        bins=[
            -0.01,
            0.25,
            0.50,
            0.75,
            1.01
        ],
        labels=[
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]
    )

    return features


# ============================================================
# FEATURE REPORT
# ============================================================

def print_feature_report(df: pd.DataFrame) -> None:
    """
    Print a summary of engineered risk features.
    """

    risk_columns = [
        "supplier_risk",
        "weather_risk",
        "traffic_risk",
        "inventory_risk",
        "warehouse_risk",
        "distance_risk",
        "transport_risk",
        "priority_risk",
        "fuel_pressure",
        "lead_time_pressure",
        "overall_risk_score"
    ]

    print("=" * 70)
    print("SUPPLY PRESCRIPT - RISK FEATURE ENGINEERING")
    print("=" * 70)

    print("\nDATASET")
    print("-" * 70)

    print(f"Records: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    print("\nENGINEERED FEATURES")
    print("-" * 70)

    for column in risk_columns:
        if column in df.columns:
            print(f"- {column}")

    print("\nRISK CATEGORY DISTRIBUTION")
    print("-" * 70)

    if "risk_category" in df.columns:

        distribution = (
            df["risk_category"]
            .value_counts()
            .sort_index()
        )

        for category, count in distribution.items():
            print(
                f"{str(category):<12}: {count:,}"
            )

    print("\nFEATURE STATISTICS")
    print("-" * 70)

    available_columns = [
        column
        for column in risk_columns
        if column in df.columns
    ]

    statistics = (
        df[available_columns]
        .describe()
        .round(3)
    )

    print(statistics.to_string())

    print("\n" + "=" * 70)
    print("FEATURE ENGINEERING COMPLETED")
    print("=" * 70)


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    input_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "cleaned_shipments.csv"
    )

    df = pd.read_csv(input_file)

    feature_df = create_risk_features(df)

    print_feature_report(feature_df)