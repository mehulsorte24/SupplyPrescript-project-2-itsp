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
# DELAY DISTRIBUTION ANALYSIS
# ============================================================

def analyze_delay_distribution(input_file: str) -> dict:
    """
    Analyze the distribution of shipment delays.

    Parameters
    ----------
    input_file : str
        Path to the processed shipment CSV file.

    Returns
    -------
    dict
        Delay distribution analysis results.
    """

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(input_file)

    # --------------------------------------------------------
    # Basic counts
    # --------------------------------------------------------

    total_shipments = len(df)

    delayed_shipments = int(
        (df["delay_status"] == "DELAYED").sum()
    )

    on_time_shipments = int(
        (df["delay_status"] == "ON_TIME").sum()
    )

    # --------------------------------------------------------
    # Delay rate
    # --------------------------------------------------------

    if total_shipments > 0:
        delay_rate = round(
            (delayed_shipments / total_shipments) * 100,
            2
        )
    else:
        delay_rate = 0.0

    # --------------------------------------------------------
    # Actual delay statistics
    # --------------------------------------------------------

    delay_series = df["actual_delay_days"]

    average_delay = round(
        float(delay_series.mean()),
        2
    )

    median_delay = round(
        float(delay_series.median()),
        2
    )

    minimum_delay = int(
        delay_series.min()
    )

    maximum_delay = int(
        delay_series.max()
    )

    # --------------------------------------------------------
    # Delayed shipments only
    # --------------------------------------------------------

    delayed_only = df.loc[
        df["delay_status"] == "DELAYED",
        "actual_delay_days"
    ]

    if len(delayed_only) > 0:

        average_delayed_days = round(
            float(delayed_only.mean()),
            2
        )

        median_delayed_days = round(
            float(delayed_only.median()),
            2
        )

    else:

        average_delayed_days = 0.0
        median_delayed_days = 0.0

    # --------------------------------------------------------
    # Delay day distribution
    # --------------------------------------------------------

    delay_distribution = (
        df["actual_delay_days"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    delay_distribution = {
        int(day): int(count)
        for day, count in delay_distribution.items()
    }

    # --------------------------------------------------------
    # Delay status distribution
    # --------------------------------------------------------

    status_distribution = (
        df["delay_status"]
        .value_counts()
        .to_dict()
    )

    status_distribution = {
        str(status): int(count)
        for status, count in status_distribution.items()
    }

    # --------------------------------------------------------
    # Create analysis report
    # --------------------------------------------------------

    analysis = {

        "total_shipments": total_shipments,

        "delayed_shipments": delayed_shipments,

        "on_time_shipments": on_time_shipments,

        "delay_rate_percent": delay_rate,

        "overall_delay_statistics": {
            "average_delay_days": average_delay,
            "median_delay_days": median_delay,
            "minimum_delay_days": minimum_delay,
            "maximum_delay_days": maximum_delay
        },

        "delayed_shipments_statistics": {
            "average_delay_days": average_delayed_days,
            "median_delay_days": median_delayed_days
        },

        "delay_day_distribution": delay_distribution,

        "status_distribution": status_distribution
    }

    return analysis


# ============================================================
# PRINT ANALYSIS REPORT
# ============================================================

def print_delay_analysis(analysis: dict) -> None:
    """
    Print a human-readable delay analysis report.
    """

    print("=" * 70)
    print("SUPPLY PRESCRIPT - DELAY DISTRIBUTION ANALYSIS")
    print("=" * 70)

    # --------------------------------------------------------
    # Shipment summary
    # --------------------------------------------------------

    print("\nSHIPMENT SUMMARY")
    print("-" * 70)

    print(
        f"Total shipments     : "
        f"{analysis['total_shipments']:,}"
    )

    print(
        f"Delayed shipments   : "
        f"{analysis['delayed_shipments']:,}"
    )

    print(
        f"On-time shipments   : "
        f"{analysis['on_time_shipments']:,}"
    )

    print(
        f"Delay rate          : "
        f"{analysis['delay_rate_percent']:.2f}%"
    )

    # --------------------------------------------------------
    # Overall delay statistics
    # --------------------------------------------------------

    overall = analysis[
        "overall_delay_statistics"
    ]

    print("\nOVERALL DELAY STATISTICS")
    print("-" * 70)

    print(
        f"Average delay      : "
        f"{overall['average_delay_days']:.2f} days"
    )

    print(
        f"Median delay       : "
        f"{overall['median_delay_days']:.2f} days"
    )

    print(
        f"Minimum delay      : "
        f"{overall['minimum_delay_days']} days"
    )

    print(
        f"Maximum delay      : "
        f"{overall['maximum_delay_days']} days"
    )

    # --------------------------------------------------------
    # Delayed shipment statistics
    # --------------------------------------------------------

    delayed = analysis[
        "delayed_shipments_statistics"
    ]

    print("\nDELAYED SHIPMENTS ONLY")
    print("-" * 70)

    print(
        f"Average delay      : "
        f"{delayed['average_delay_days']:.2f} days"
    )

    print(
        f"Median delay       : "
        f"{delayed['median_delay_days']:.2f} days"
    )

    # --------------------------------------------------------
    # Status distribution
    # --------------------------------------------------------

    print("\nSTATUS DISTRIBUTION")
    print("-" * 70)

    for status, count in analysis[
        "status_distribution"
    ].items():

        print(
            f"{status:<20}: {count:,}"
        )

    # --------------------------------------------------------
    # Delay day distribution
    # --------------------------------------------------------

    print("\nDELAY DAYS DISTRIBUTION")
    print("-" * 70)

    for day, count in analysis[
        "delay_day_distribution"
    ].items():

        print(
            f"{day:>2} day(s)           : {count:,}"
        )

    print("\n" + "=" * 70)
    print("DELAY ANALYSIS COMPLETED")
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

    analysis = analyze_delay_distribution(
        str(input_file)
    )

    print_delay_analysis(analysis)