from pathlib import Path
import json
import sys
from datetime import datetime, timezone

import pandas as pd


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# FILE CONFIGURATION
# ============================================================

DRIFT_REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "drift_detection_report.json"
)

HISTORY_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "drift_history.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "drift_trend_report.json"
)


# ============================================================
# TREND CONFIGURATION
# ============================================================

# Number of previous drift observations retained.
MAX_HISTORY_RECORDS = 50

# Minimum number of observations required before
# a meaningful trend can be calculated.
MIN_TREND_OBSERVATIONS = 2

# Change in drift percentage required to classify
# the trend as worsening or improving.
TREND_CHANGE_THRESHOLD = 5.0


# ============================================================
# FILE LOADING FUNCTIONS
# ============================================================

def load_drift_report() -> dict:
    """
    Load the latest drift detection report.
    """

    print("Loading latest drift detection report...")

    if not DRIFT_REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Drift detection report not found: "
            f"{DRIFT_REPORT_FILE}"
        )

    try:
        with open(
            DRIFT_REPORT_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            report = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Drift detection report contains invalid JSON: "
            f"{error}"
        )

    print("   ✓ Drift detection report found.")

    return report


def load_history() -> list:
    """
    Load existing drift history.

    If no history exists, start with an empty history.
    """

    if not HISTORY_FILE.exists():
        print(
            "   No previous drift history found."
        )
        print(
            "   Starting a new drift history."
        )

        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            history = json.load(file)

    except json.JSONDecodeError:
        print(
            "   ⚠ Existing drift history is invalid."
        )
        print(
            "   Starting a new drift history."
        )

        return []

    if not isinstance(history, list):
        print(
            "   ⚠ Drift history format is invalid."
        )
        print(
            "   Starting a new drift history."
        )

        return []

    print(
        f"   ✓ Existing drift history found: "
        f"{len(history)} records."
    )

    return history


# ============================================================
# HISTORY MANAGEMENT
# ============================================================

def create_history_record(
    drift_report: dict,
) -> dict:
    """
    Convert the latest drift report into a compact
    historical observation.
    """

    summary = drift_report.get(
        "summary",
        {},
    )

    feature_results = drift_report.get(
        "feature_results",
        [],
    )

    drifted_features = [
        result.get("feature")
        for result in feature_results
        if result.get("drift_detected") is True
    ]

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "model_version": drift_report.get(
            "model_version",
            "unknown",
        ),
        "total_records": drift_report.get(
            "dataset",
            {},
        ).get(
            "total_records",
            0,
        ),
        "features_checked": summary.get(
            "total_features_checked",
            0,
        ),
        "stable_features": summary.get(
            "stable_features",
            0,
        ),
        "drifted_features": summary.get(
            "drifted_features",
            0,
        ),
        "drift_percentage": summary.get(
            "drift_percentage",
            0.0,
        ),
        "overall_status": summary.get(
            "overall_status",
            "UNKNOWN",
        ),
        "retraining_signal": summary.get(
            "retraining_signal",
            False,
        ),
        "drifted_feature_names": drifted_features,
    }


def append_history(
    history: list,
    new_record: dict,
) -> list:
    """
    Append the current observation and retain only
    the configured number of historical records.
    """

    history.append(new_record)

    if len(history) > MAX_HISTORY_RECORDS:
        history = history[-MAX_HISTORY_RECORDS:]

    return history


def save_history(history: list) -> None:
    """
    Save historical drift observations.
    """

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history,
            file,
            indent=4,
        )

    print("\n✓ Drift history saved:")
    print(f"  {HISTORY_FILE}")


# ============================================================
# TREND ANALYSIS
# ============================================================

def calculate_trend(
    history: list,
) -> dict:
    """
    Compare the latest drift percentage with the
    previous observation.
    """

    if len(history) < MIN_TREND_OBSERVATIONS:
        return {
            "trend": "INSUFFICIENT_HISTORY",
            "previous_drift_percentage": None,
            "current_drift_percentage": (
                history[-1]["drift_percentage"]
                if history
                else None
            ),
            "change_percentage_points": None,
            "interpretation": (
                "A second drift observation is required "
                "to determine the trend."
            ),
        }

    previous = history[-2]
    current = history[-1]

    previous_percentage = float(
        previous.get(
            "drift_percentage",
            0.0,
        )
    )

    current_percentage = float(
        current.get(
            "drift_percentage",
            0.0,
        )
    )

    change = (
        current_percentage
        - previous_percentage
    )

    if change >= TREND_CHANGE_THRESHOLD:
        trend = "WORSENING"

        interpretation = (
            "Data drift has increased significantly "
            "compared with the previous observation."
        )

    elif change <= -TREND_CHANGE_THRESHOLD:
        trend = "IMPROVING"

        interpretation = (
            "Data drift has decreased significantly "
            "compared with the previous observation."
        )

    else:
        trend = "STABLE"

        interpretation = (
            "Data drift remains relatively stable "
            "compared with the previous observation."
        )

    return {
        "trend": trend,
        "previous_drift_percentage": round(
            previous_percentage,
            2,
        ),
        "current_drift_percentage": round(
            current_percentage,
            2,
        ),
        "change_percentage_points": round(
            change,
            2,
        ),
        "interpretation": interpretation,
    }


def analyze_feature_history(
    history: list,
) -> dict:
    """
    Identify features that repeatedly appear as drifted
    across historical observations.
    """

    feature_counts = {}

    for record in history:
        drifted_features = record.get(
            "drifted_feature_names",
            [],
        )

        for feature in drifted_features:
            feature_counts[feature] = (
                feature_counts.get(feature, 0)
                + 1
            )

    repeated_features = {
        feature: count
        for feature, count in feature_counts.items()
        if count >= 2
    }

    return {
        "total_features_with_historical_drift": len(
            feature_counts
        ),
        "repeatedly_drifted_features": (
            repeated_features
        ),
        "most_frequent_drift_features": sorted(
            feature_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5],
    }


# ============================================================
# OPERATIONAL RECOMMENDATION
# ============================================================

def generate_recommendation(
    latest_status: str,
    trend: str,
    retraining_signal: bool,
    repeated_features: dict,
) -> str:
    """
    Generate an operational recommendation based on
    current drift, trend, and historical behaviour.
    """

    if retraining_signal:
        return (
            "REVIEW_RETRAINING: "
            "The latest drift detection produced a "
            "retraining signal. Evaluate model performance "
            "and retrain when appropriate."
        )

    if latest_status == "HIGH_DRIFT":
        return (
            "HIGH_DRIFT_MONITORING: "
            "Significant feature drift is present. "
            "Review model performance before continuing "
            "normal operation."
        )

    if trend == "WORSENING":
        return (
            "INCREASED_MONITORING: "
            "Data drift is worsening. Increase monitoring "
            "frequency and evaluate prediction quality."
        )

    if repeated_features:
        return (
            "REPEATED_FEATURE_DRIFT: "
            "Some features repeatedly show drift. "
            "Investigate their data generation and "
            "distribution changes."
        )

    if trend == "IMPROVING":
        return (
            "DRIFT_IMPROVING: "
            "Data distribution is moving closer to the "
            "historical reference. Continue monitoring."
        )

    return (
        "NORMAL_MONITORING: "
        "No significant persistent drift pattern detected."
    )


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(
    drift_report: dict,
    history: list,
) -> dict:
    """
    Generate the complete drift trend report.
    """

    trend_analysis = calculate_trend(
        history
    )

    feature_history = analyze_feature_history(
        history
    )

    latest_summary = drift_report.get(
        "summary",
        {},
    )

    latest_status = latest_summary.get(
        "overall_status",
        "UNKNOWN",
    )

    retraining_signal = latest_summary.get(
        "retraining_signal",
        False,
    )

    repeated_features = feature_history.get(
        "repeatedly_drifted_features",
        {},
    )

    recommendation = generate_recommendation(
        latest_status=latest_status,
        trend=trend_analysis["trend"],
        retraining_signal=retraining_signal,
        repeated_features=repeated_features,
    )

    return {
        "engine": (
            "AI Model Drift History and Trend Engine"
        ),
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "model_version": drift_report.get(
            "model_version",
            "unknown",
        ),
        "latest_observation": {
            "drift_percentage": latest_summary.get(
                "drift_percentage",
                0.0,
            ),
            "drifted_features": latest_summary.get(
                "drifted_features",
                0,
            ),
            "stable_features": latest_summary.get(
                "stable_features",
                0,
            ),
            "overall_status": latest_status,
            "retraining_signal": retraining_signal,
        },
        "history": {
            "observations": len(history),
            "maximum_retained_observations": (
                MAX_HISTORY_RECORDS
            ),
        },
        "trend_analysis": trend_analysis,
        "feature_history": feature_history,
        "recommendation": recommendation,
    }


def save_report(report: dict) -> None:
    """
    Save the drift trend report.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
        )

    print("\n✓ Drift trend report saved:")
    print(f"  {OUTPUT_FILE}")


# ============================================================
# MAIN ENGINE
# ============================================================

def run_drift_history_engine() -> dict:
    """
    Execute the complete drift history and trend workflow.
    """

    drift_report = load_drift_report()

    print("\nLoading drift history...")

    history = load_history()

    print("\nCreating current drift observation...")

    current_record = create_history_record(
        drift_report
    )

    history = append_history(
        history,
        current_record,
    )

    print(
        f"   ✓ Current observation added."
    )

    trend_analysis = calculate_trend(
        history
    )

    feature_history = analyze_feature_history(
        history
    )

    report = generate_report(
        drift_report,
        history,
    )

    save_history(history)
    save_report(report)

    print("\n" + "=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI MODEL DRIFT HISTORY "
        "AND TREND ENGINE"
    )
    print("=" * 90)

    print(
        f"\nModel Version: "
        f"{report['model_version']}"
    )

    print(
        f"Historical Observations: "
        f"{len(history)}"
    )

    print(
        f"Latest Drift: "
        f"{report['latest_observation']['drift_percentage']:.2f}%"
    )

    print(
        f"Latest Status: "
        f"{report['latest_observation']['overall_status']}"
    )

    print(
        f"Drift Trend: "
        f"{trend_analysis['trend']}"
    )

    if (
        trend_analysis[
            "change_percentage_points"
        ]
        is not None
    ):
        print(
            f"Drift Change: "
            f"{trend_analysis['change_percentage_points']:+.2f} "
            f"percentage points"
        )

    print(
        f"Features With Historical Drift: "
        f"{feature_history['total_features_with_historical_drift']}"
    )

    repeated_features = feature_history[
        "repeatedly_drifted_features"
    ]

    if repeated_features:
        print(
            "\nRepeatedly Drifted Features:"
        )

        for feature, count in repeated_features.items():
            print(
                f"   {feature}: "
                f"{count} observations"
            )
    else:
        print(
            "\nRepeatedly Drifted Features:"
        )
        print(
            "   None detected yet."
        )

    print(
        "\nOperational Recommendation:"
    )

    print(
        f"   {report['recommendation']}"
    )

    print("\n" + "=" * 90)

    print(
        "\nAI MODEL DRIFT HISTORY AND TREND ENGINE "
        "COMPLETED"
    )

    return report


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        run_drift_history_engine()

    except FileNotFoundError as error:
        print("\n✗ File Error:")
        print(f"  {error}")

        sys.exit(1)

    except ValueError as error:
        print("\n✗ Data Error:")
        print(f"  {error}")

        sys.exit(1)

    except Exception as error:
        print("\n✗ Unexpected Error:")
        print(f"  {error}")

        sys.exit(1)