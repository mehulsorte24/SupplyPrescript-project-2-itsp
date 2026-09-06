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
# IMPORT FEATURE ENGINEERING
# ============================================================

from ai_engine.features.risk_features import create_risk_features


# ============================================================
# ML FEATURE CONFIGURATION
# ============================================================

ML_FEATURE_COLUMNS = [
    "distance_km",
    "lead_time_days",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "fuel_price_index",
    "warehouse_load",
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


TARGET_COLUMNS = [
    "delay_status",
    "actual_delay_days"
]


IDENTIFIER_COLUMNS = [
    "shipment_id",
    "supplier_id",
    "origin",
    "destination",
    "transport_mode",
    "weather_severity",
    "traffic_level",
    "priority",
    "generated_at"
]


# ============================================================
# FEATURE PIPELINE
# ============================================================

def build_feature_dataset(input_file: str) -> pd.DataFrame:
    """
    Build an ML-ready feature dataset from cleaned shipment data.

    Parameters
    ----------
    input_file : str
        Path to the cleaned shipment CSV.

    Returns
    -------
    pd.DataFrame
        Dataset containing identifiers, ML features, and targets.
    """

    # --------------------------------------------------------
    # Load cleaned dataset
    # --------------------------------------------------------

    df = pd.read_csv(input_file)

    print(f"Loaded records: {len(df):,}")

    # --------------------------------------------------------
    # Create engineered features
    # --------------------------------------------------------

    feature_df = create_risk_features(df)

    print(
        f"Features after engineering: "
        f"{len(feature_df.columns):,}"
    )

    # --------------------------------------------------------
    # Verify required feature columns
    # --------------------------------------------------------

    required_columns = (
        IDENTIFIER_COLUMNS
        + ML_FEATURE_COLUMNS
        + TARGET_COLUMNS
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in feature_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required feature columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Select ML-ready dataset
    # --------------------------------------------------------

    selected_columns = (
        IDENTIFIER_COLUMNS
        + ML_FEATURE_COLUMNS
        + TARGET_COLUMNS
    )

    ml_dataset = feature_df[selected_columns].copy()

    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    ml_dataset = ml_dataset.reset_index(drop=True)

    return ml_dataset


# ============================================================
# SAVE FEATURE DATASET
# ============================================================

def save_feature_dataset(
    df: pd.DataFrame,
    output_file: str
) -> None:
    """
    Save the ML-ready feature dataset.
    """

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"✓ Feature dataset saved to: "
        f"{output_path}"
    )


# ============================================================
# PRINT FEATURE PIPELINE REPORT
# ============================================================

def print_feature_pipeline_report(
    df: pd.DataFrame
) -> None:
    """
    Print a summary of the generated ML-ready dataset.
    """

    print("=" * 70)
    print("SUPPLY PRESCRIPT - ML FEATURE PIPELINE")
    print("=" * 70)

    print("\nDATASET SUMMARY")
    print("-" * 70)

    print(
        f"Records             : "
        f"{len(df):,}"
    )

    print(
        f"Total columns       : "
        f"{len(df.columns):,}"
    )

    print(
        f"ML features         : "
        f"{len(ML_FEATURE_COLUMNS):,}"
    )

    print(
        f"Target columns      : "
        f"{len(TARGET_COLUMNS):,}"
    )

    print(
        f"Identifier columns  : "
        f"{len(IDENTIFIER_COLUMNS):,}"
    )

    # --------------------------------------------------------
    # ML features
    # --------------------------------------------------------

    print("\nML FEATURES")
    print("-" * 70)

    for index, column in enumerate(
        ML_FEATURE_COLUMNS,
        start=1
    ):
        print(
            f"{index:>2}. {column}"
        )

    # --------------------------------------------------------
    # Targets
    # --------------------------------------------------------

    print("\nTARGET VARIABLES")
    print("-" * 70)

    for index, column in enumerate(
        TARGET_COLUMNS,
        start=1
    ):
        print(
            f"{index:>2}. {column}"
        )

    # --------------------------------------------------------
    # Dataset preview
    # --------------------------------------------------------

    print("\nFEATURE DATASET PREVIEW")
    print("-" * 70)

    print(
        df[
            ML_FEATURE_COLUMNS + TARGET_COLUMNS
        ].head(5).to_string()
    )

    # --------------------------------------------------------
    # Missing value check
    # --------------------------------------------------------

    total_missing = int(
        df.isnull().sum().sum()
    )

    print("\nDATA QUALITY CHECK")
    print("-" * 70)

    print(
        f"Missing values     : "
        f"{total_missing:,}"
    )

    print(
        f"Duplicate rows     : "
        f"{df.duplicated().sum():,}"
    )

    # --------------------------------------------------------
    # Target distribution
    # --------------------------------------------------------

    if "delay_status" in df.columns:

        print("\nTARGET DISTRIBUTION")
        print("-" * 70)

        status_counts = (
            df["delay_status"]
            .value_counts()
        )

        for status, count in status_counts.items():

            percentage = (
                count / len(df) * 100
                if len(df) > 0
                else 0
            )

            print(
                f"{status:<15}: "
                f"{count:>6,} "
                f"({percentage:.2f}%)"
            )

    print("\n" + "=" * 70)
    print("ML FEATURE PIPELINE COMPLETED")
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

    output_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "ml_features.csv"
    )

    ml_dataset = build_feature_dataset(
        str(input_file)
    )

    save_feature_dataset(
        ml_dataset,
        str(output_file)
    )

    print_feature_pipeline_report(
        ml_dataset
    )