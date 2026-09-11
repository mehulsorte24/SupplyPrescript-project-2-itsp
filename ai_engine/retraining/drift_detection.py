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

FEATURE_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "data"
    / "processed"
    / "ml_features.csv"
)

MODEL_METADATA_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "models"
    / "classifier_metadata.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "drift_detection_report.json"
)


# ============================================================
# DRIFT CONFIGURATION
# ============================================================

# Percentage difference threshold used for numeric features.
NUMERIC_DRIFT_THRESHOLD = 0.20

# Category distribution difference threshold.
CATEGORICAL_DRIFT_THRESHOLD = 0.20

# If this percentage of features drift, overall drift is HIGH.
HIGH_DRIFT_FEATURE_PERCENTAGE = 0.40

# If this percentage of features drift, overall drift is MODERATE.
MODERATE_DRIFT_FEATURE_PERCENTAGE = 0.20


# ============================================================
# EXPECTED AI FEATURES
# ============================================================

NUMERIC_FEATURES = [
    "distance_km",
    "lead_time_days",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "fuel_price_index",
    "warehouse_load",
]

CATEGORICAL_FEATURES = [
    "transport_mode",
    "weather_severity",
    "traffic_level",
    "priority",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_feature_data() -> pd.DataFrame:
    """
    Load the machine-learning feature dataset.
    """

    print("Loading ML feature dataset...")

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"ML feature file not found: {FEATURE_FILE}"
        )

    df = pd.read_csv(FEATURE_FILE)

    if df.empty:
        raise ValueError("ML feature dataset is empty.")

    print(f"   ✓ Feature dataset found.")
    print(f"   Records available: {len(df)}")

    return df


def load_model_metadata() -> dict:
    """
    Load classifier metadata when available.

    Metadata is used as supporting information for the
    drift report. The engine can still operate if metadata
    is unavailable.
    """

    print("\nLoading model metadata...")

    if not MODEL_METADATA_FILE.exists():
        print("   ⚠ Model metadata not found.")
        print("   Continuing without metadata.")

        return {}

    try:
        with open(MODEL_METADATA_FILE, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        print("   ✓ Model metadata found.")

        return metadata

    except json.JSONDecodeError:
        print("   ⚠ Model metadata is not valid JSON.")
        print("   Continuing without metadata.")

        return {}


def calculate_numeric_drift(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Calculate a simple distribution drift score for a numeric
    feature.

    The dataset is divided into two time-ordered portions:

        Reference data = older records
        Current data   = newer records

    The mean of the two portions is compared using relative
    difference.
    """

    if column not in df.columns:
        return {
            "feature": column,
            "type": "numeric",
            "status": "MISSING",
            "drift_score": None,
            "drift_detected": False,
            "reason": "Feature not found in dataset.",
        }

    values = pd.to_numeric(df[column], errors="coerce").dropna()

    if len(values) < 10:
        return {
            "feature": column,
            "type": "numeric",
            "status": "INSUFFICIENT_DATA",
            "drift_score": None,
            "drift_detected": False,
            "reason": "Not enough observations for drift analysis.",
        }

    split_index = len(values) // 2

    reference = values.iloc[:split_index]
    current = values.iloc[split_index:]

    reference_mean = float(reference.mean())
    current_mean = float(current.mean())

    denominator = max(abs(reference_mean), 1e-9)

    drift_score = abs(
        current_mean - reference_mean
    ) / denominator

    drift_detected = drift_score >= NUMERIC_DRIFT_THRESHOLD

    if drift_detected:
        status = "DRIFT_DETECTED"
    else:
        status = "STABLE"

    return {
        "feature": column,
        "type": "numeric",
        "status": status,
        "drift_score": round(float(drift_score), 4),
        "drift_detected": bool(drift_detected),
        "reference_mean": round(reference_mean, 4),
        "current_mean": round(current_mean, 4),
        "threshold": NUMERIC_DRIFT_THRESHOLD,
    }


def calculate_categorical_drift(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Calculate categorical distribution drift.

    The maximum absolute change in category share between
    the older and newer portions of the dataset is used
    as the drift score.
    """

    if column not in df.columns:
        return {
            "feature": column,
            "type": "categorical",
            "status": "MISSING",
            "drift_score": None,
            "drift_detected": False,
            "reason": "Feature not found in dataset.",
        }

    values = (
        df[column]
        .astype("string")
        .fillna("UNKNOWN")
    )

    if len(values) < 10:
        return {
            "feature": column,
            "type": "categorical",
            "status": "INSUFFICIENT_DATA",
            "drift_score": None,
            "drift_detected": False,
            "reason": "Not enough observations for drift analysis.",
        }

    split_index = len(values) // 2

    reference = values.iloc[:split_index]
    current = values.iloc[split_index:]

    reference_distribution = reference.value_counts(
        normalize=True
    )

    current_distribution = current.value_counts(
        normalize=True
    )

    all_categories = set(reference_distribution.index).union(
        set(current_distribution.index)
    )

    max_difference = 0.0

    for category in all_categories:
        reference_share = float(
            reference_distribution.get(category, 0.0)
        )

        current_share = float(
            current_distribution.get(category, 0.0)
        )

        difference = abs(
            current_share - reference_share
        )

        max_difference = max(
            max_difference,
            difference,
        )

    drift_detected = (
        max_difference >= CATEGORICAL_DRIFT_THRESHOLD
    )

    if drift_detected:
        status = "DRIFT_DETECTED"
    else:
        status = "STABLE"

    return {
        "feature": column,
        "type": "categorical",
        "status": status,
        "drift_score": round(float(max_difference), 4),
        "drift_detected": bool(drift_detected),
        "threshold": CATEGORICAL_DRIFT_THRESHOLD,
        "reference_categories": int(
            reference.nunique()
        ),
        "current_categories": int(
            current.nunique()
        ),
    }


def determine_overall_status(
    feature_results: list,
) -> tuple[str, bool]:
    """
    Determine overall dataset drift status.
    """

    valid_results = [
        result
        for result in feature_results
        if result.get("drift_score") is not None
    ]

    if not valid_results:
        return "INSUFFICIENT_DATA", False

    drifted_features = [
        result
        for result in valid_results
        if result.get("drift_detected") is True
    ]

    drift_percentage = (
        len(drifted_features)
        / len(valid_results)
    )

    if drift_percentage >= HIGH_DRIFT_FEATURE_PERCENTAGE:
        return "HIGH_DRIFT", True

    if drift_percentage >= MODERATE_DRIFT_FEATURE_PERCENTAGE:
        return "MODERATE_DRIFT", True

    return "STABLE", False


def generate_recommendation(
    overall_status: str,
    drift_percentage: float,
) -> str:
    """
    Generate an operational recommendation from the drift status.
    """

    if overall_status == "HIGH_DRIFT":
        return (
            "SIGNIFICANT_DATA_DRIFT_DETECTED: "
            "Review incoming data and trigger model retraining "
            "if prediction performance has degraded."
        )

    if overall_status == "MODERATE_DRIFT":
        return (
            "MODERATE_DATA_DRIFT_DETECTED: "
            "Increase monitoring frequency and evaluate model "
            "performance before retraining."
        )

    if overall_status == "STABLE":
        return (
            "NO_SIGNIFICANT_DATA_DRIFT: "
            "Continue normal model monitoring."
        )

    return (
        "DRIFT_ANALYSIS_INCOMPLETE: "
        "Collect additional feature data before making "
        "a retraining decision."
    )


def save_report(report: dict) -> None:
    """
    Save the drift detection report as JSON.
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

    print("\n✓ Drift detection report saved:")
    print(f"  {OUTPUT_FILE}")


# ============================================================
# MAIN DRIFT DETECTION ENGINE
# ============================================================

def run_drift_detection() -> dict:
    """
    Execute the complete AI data drift detection workflow.
    """

    df = load_feature_data()
    metadata = load_model_metadata()

    print("\nAnalyzing feature distributions...")

    feature_results = []

    for feature in NUMERIC_FEATURES:
        result = calculate_numeric_drift(
            df,
            feature,
        )

        feature_results.append(result)

    for feature in CATEGORICAL_FEATURES:
        result = calculate_categorical_drift(
            df,
            feature,
        )

        feature_results.append(result)

    valid_results = [
        result
        for result in feature_results
        if result.get("drift_score") is not None
    ]

    drifted_results = [
        result
        for result in valid_results
        if result.get("drift_detected") is True
    ]

    stable_results = [
        result
        for result in valid_results
        if result.get("drift_detected") is False
    ]

    if valid_results:
        drift_percentage = (
            len(drifted_results)
            / len(valid_results)
        )
    else:
        drift_percentage = 0.0

    overall_status, retraining_signal = (
        determine_overall_status(
            feature_results
        )
    )

    recommendation = generate_recommendation(
        overall_status,
        drift_percentage,
    )

    current_model_version = metadata.get(
        "model_version",
        metadata.get(
            "version",
            "v1.0",
        ),
    )

    report = {
        "engine": "AI Model Data Drift Detection Engine",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "model_version": current_model_version,
        "dataset": {
            "file": str(FEATURE_FILE),
            "total_records": int(len(df)),
            "reference_records": int(len(df) // 2),
            "current_records": int(
                len(df) - (len(df) // 2)
            ),
        },
        "thresholds": {
            "numeric_drift_threshold": (
                NUMERIC_DRIFT_THRESHOLD
            ),
            "categorical_drift_threshold": (
                CATEGORICAL_DRIFT_THRESHOLD
            ),
            "moderate_drift_feature_percentage": (
                MODERATE_DRIFT_FEATURE_PERCENTAGE
            ),
            "high_drift_feature_percentage": (
                HIGH_DRIFT_FEATURE_PERCENTAGE
            ),
        },
        "summary": {
            "total_features_checked": int(
                len(feature_results)
            ),
            "features_with_valid_analysis": int(
                len(valid_results)
            ),
            "stable_features": int(
                len(stable_results)
            ),
            "drifted_features": int(
                len(drifted_results)
            ),
            "drift_percentage": round(
                drift_percentage * 100,
                2,
            ),
            "overall_status": overall_status,
            "retraining_signal": bool(
                retraining_signal
            ),
        },
        "feature_results": feature_results,
        "drifted_features": [
            result["feature"]
            for result in drifted_results
        ],
        "recommendation": recommendation,
    }

    print("\n" + "=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI MODEL DATA DRIFT DETECTION ENGINE"
    )
    print("=" * 90)

    print(
        f"\nCurrent Model Version: "
        f"{current_model_version}"
    )

    print(
        f"Overall Drift Status: "
        f"{overall_status}"
    )

    print(
        f"\nFeatures Checked: "
        f"{len(feature_results)}"
    )

    print(
        f"Stable Features: "
        f"{len(stable_results)}"
    )

    print(
        f"Drifted Features: "
        f"{len(drifted_results)}"
    )

    print(
        f"Drift Percentage: "
        f"{drift_percentage * 100:.2f}%"
    )

    print("\nFeature Drift Results:")

    for result in feature_results:
        feature = result["feature"]
        status = result["status"]
        score = result["drift_score"]

        if score is None:
            score_text = "N/A"
        else:
            score_text = f"{score:.4f}"

        print(
            f"   {feature}: "
            f"{status} "
            f"(score: {score_text})"
        )

    print("\nRetraining Signal:")

    if retraining_signal:
        print(
            "   ⚠ REVIEW RETRAINING"
        )
    else:
        print(
            "   ✓ NO IMMEDIATE RETRAINING SIGNAL"
        )

    print(
        f"\nRecommendation:\n"
        f"   {recommendation}"
    )

    print("\n" + "=" * 90)

    save_report(report)

    print(
        "\nAI MODEL DATA DRIFT DETECTION ENGINE COMPLETED"
    )

    return report


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        run_drift_detection()

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