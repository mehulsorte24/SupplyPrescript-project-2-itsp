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
# DATA PROFILING FUNCTION
# ============================================================

def profile_shipments(input_file: str) -> dict:
    """
    Generate a quality and statistical profile of shipment data.

    Parameters
    ----------
    input_file : str
        Path to the shipment CSV file.

    Returns
    -------
    dict
        Dataset profiling information.
    """

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(input_file)

    # --------------------------------------------------------
    # Basic dataset information
    # --------------------------------------------------------

    row_count = len(df)
    column_count = len(df.columns)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = df.isnull().sum()

    missing_values = {
        column: int(count)
        for column, count in missing_values.items()
        if count > 0
    }

    total_missing_values = int(
        df.isnull().sum().sum()
    )

    # --------------------------------------------------------
    # Duplicate shipment IDs
    # --------------------------------------------------------

    duplicate_count = int(
        df["shipment_id"].duplicated().sum()
    )

    # --------------------------------------------------------
    # Numeric statistics
    # --------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    numeric_statistics = {}

    if numeric_columns:
        numeric_statistics = (
            df[numeric_columns]
            .describe()
            .round(2)
            .to_dict()
        )

    # --------------------------------------------------------
    # Categorical statistics
    # --------------------------------------------------------

    categorical_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    categorical_statistics = {}

    for column in categorical_columns:
        categorical_statistics[column] = (
            df[column]
            .value_counts(dropna=False)
            .to_dict()
        )

    # --------------------------------------------------------
    # Delay statistics
    # --------------------------------------------------------

    delayed_records = 0
    on_time_records = 0
    average_delay_days = 0.0
    maximum_delay_days = 0

    if "delay_status" in df.columns:

        delayed_records = int(
            (df["delay_status"] == "DELAYED").sum()
        )

        on_time_records = int(
            (df["delay_status"] == "ON_TIME").sum()
        )

    if "actual_delay_days" in df.columns:

        average_delay_days = round(
            float(df["actual_delay_days"].mean()),
            2
        )

        maximum_delay_days = int(
            df["actual_delay_days"].max()
        )

    # --------------------------------------------------------
    # Delay rate
    # --------------------------------------------------------

    delay_rate = 0.0

    if row_count > 0:
        delay_rate = round(
            (delayed_records / row_count) * 100,
            2
        )

    # --------------------------------------------------------
    # Create profile report
    # --------------------------------------------------------

    profile = {
        "dataset": {
            "rows": row_count,
            "columns": column_count,
            "column_names": df.columns.tolist()
        },

        "quality": {
            "total_missing_values": total_missing_values,
            "missing_values": missing_values,
            "duplicate_shipment_ids": duplicate_count
        },

        "numeric_statistics": numeric_statistics,

        "categorical_statistics": categorical_statistics,

        "delay_statistics": {
            "total_shipments": row_count,
            "delayed_shipments": delayed_records,
            "on_time_shipments": on_time_records,
            "delay_rate_percent": delay_rate,
            "average_delay_days": average_delay_days,
            "maximum_delay_days": maximum_delay_days
        }
    }

    return profile


# ============================================================
# PRINT PROFILE REPORT
# ============================================================

def print_profile_report(profile: dict) -> None:
    """
    Print a human-readable shipment dataset profile.
    """

    print("=" * 70)
    print("SUPPLY PRESCRIPT - DATASET PROFILE")
    print("=" * 70)

    # --------------------------------------------------------
    # Dataset overview
    # --------------------------------------------------------

    dataset = profile["dataset"]

    print("\nDATASET OVERVIEW")
    print("-" * 70)
    print(f"Rows              : {dataset['rows']:,}")
    print(f"Columns           : {dataset['columns']:,}")

    # --------------------------------------------------------
    # Data quality
    # --------------------------------------------------------

    quality = profile["quality"]

    print("\nDATA QUALITY")
    print("-" * 70)
    print(
        f"Missing values    : "
        f"{quality['total_missing_values']:,}"
    )
    print(
        f"Duplicate IDs     : "
        f"{quality['duplicate_shipment_ids']:,}"
    )

    if quality["missing_values"]:
        print("\nMissing values by column:")

        for column, count in quality["missing_values"].items():
            print(f"- {column}: {count}")

    # --------------------------------------------------------
    # Delay statistics
    # --------------------------------------------------------

    delay = profile["delay_statistics"]

    print("\nDELAY STATISTICS")
    print("-" * 70)
    print(
        f"Delayed shipments : "
        f"{delay['delayed_shipments']:,}"
    )
    print(
        f"On-time shipments : "
        f"{delay['on_time_shipments']:,}"
    )
    print(
        f"Delay rate        : "
        f"{delay['delay_rate_percent']:.2f}%"
    )
    print(
        f"Average delay     : "
        f"{delay['average_delay_days']:.2f} days"
    )
    print(
        f"Maximum delay     : "
        f"{delay['maximum_delay_days']} days"
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    print("\nNUMERIC COLUMNS")
    print("-" * 70)

    for column in profile["numeric_statistics"]:
        print(f"- {column}")

    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    print("\nCATEGORICAL COLUMNS")
    print("-" * 70)

    for column in profile["categorical_statistics"]:
        print(f"- {column}")

    print("\n" + "=" * 70)
    print("PROFILE GENERATION COMPLETED")
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

    profile = profile_shipments(
        str(input_file)
    )

    print_profile_report(profile)