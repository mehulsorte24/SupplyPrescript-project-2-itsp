from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRAINING_DIR = PROJECT_ROOT / "ai_engine" / "retraining"

VERSION_REGISTRY_FILE = RETRAINING_DIR / "model_versions.json"
RETRAINING_REPORT_FILE = RETRAINING_DIR / "retraining_report.json"

COMPARISON_REPORT_FILE = (
    RETRAINING_DIR / "model_comparison_report.json"
)


def get_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object in: {file_path}"
        )

    return data


def save_json(file_path: Path, data: Dict[str, Any]) -> None:
    """Save a dictionary as formatted JSON."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def get_current_version(
    registry: Dict[str, Any]
) -> Optional[str]:
    """Get the currently active model version."""
    current_version = registry.get("current_version")

    if current_version:
        return str(current_version)

    return None


def get_latest_version(
    registry: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Return the latest registered model version."""
    versions = registry.get("versions", [])

    if not versions:
        return None

    return versions[-1]


def extract_metrics(
    retraining_report: Dict[str, Any]
) -> Dict[str, Optional[float]]:
    """
    Extract classification and regression metrics
    from the retraining report.
    """

    classification = retraining_report.get(
        "classification_metrics",
        {}
    )

    regression = retraining_report.get(
        "regression_metrics",
        {}
    )

    return {
        "accuracy_percent": classification.get("accuracy_percent"),
        "precision_percent": classification.get("precision_percent"),
        "recall_percent": classification.get("recall_percent"),
        "f1_percent": classification.get("f1_percent"),
        "roc_auc_percent": classification.get("roc_auc_percent"),
        "mae_days": regression.get("mae_days"),
        "rmse_days": regression.get("rmse_days"),
        "r2": regression.get("r2"),
    }


def compare_metric(
    current_value: Optional[float],
    new_value: Optional[float],
    higher_is_better: bool,
) -> str:
    """
    Compare two metric values.

    Returns:
        IMPROVED
        DECLINED
        UNCHANGED
        NOT_AVAILABLE
    """

    if current_value is None or new_value is None:
        return "NOT_AVAILABLE"

    tolerance = 0.000001

    if abs(current_value - new_value) <= tolerance:
        return "UNCHANGED"

    if higher_is_better:
        return (
            "IMPROVED"
            if new_value > current_value
            else "DECLINED"
        )

    return (
        "IMPROVED"
        if new_value < current_value
        else "DECLINED"
    )


def calculate_comparison_score(
    comparisons: Dict[str, str]
) -> Dict[str, Any]:
    """Calculate an overall comparison result."""

    higher_is_better_metrics = [
        "accuracy_percent",
        "precision_percent",
        "recall_percent",
        "f1_percent",
        "roc_auc_percent",
        "r2",
    ]

    lower_is_better_metrics = [
        "mae_days",
        "rmse_days",
    ]

    improved = 0
    declined = 0
    unchanged = 0
    unavailable = 0

    for metric in (
        higher_is_better_metrics
        + lower_is_better_metrics
    ):
        result = comparisons.get(metric)

        if result == "IMPROVED":
            improved += 1
        elif result == "DECLINED":
            declined += 1
        elif result == "UNCHANGED":
            unchanged += 1
        else:
            unavailable += 1

    available = improved + declined + unchanged

    if available == 0:
        overall_result = "NOT_ENOUGH_DATA"

    elif improved > declined:
        overall_result = "IMPROVED"

    elif declined > improved:
        overall_result = "DECLINED"

    else:
        overall_result = "UNCHANGED"

    return {
        "improved_metrics": improved,
        "declined_metrics": declined,
        "unchanged_metrics": unchanged,
        "unavailable_metrics": unavailable,
        "available_metrics": available,
        "overall_result": overall_result,
    }


def create_baseline_report(
    registry: Dict[str, Any],
) -> Dict[str, Any]:
    """Create the first comparison report when only v1.0 exists."""

    current_version = get_current_version(registry)

    latest_version = get_latest_version(registry)

    if latest_version is None:
        raise ValueError(
            "No model versions are registered."
        )

    version_name = latest_version.get(
        "version",
        current_version or "v1.0",
    )

    report = {
        "system": "SupplyPrescript",
        "module": "AI Model Performance Comparison Engine",
        "generated_at": get_timestamp(),
        "comparison_type": "BASELINE",
        "current_version": current_version,
        "candidate_version": version_name,
        "decision": {
            "candidate_is_better": False,
            "recommendation": "KEEP_BASELINE",
        },
        "summary": {
            "status": "BASELINE_ESTABLISHED",
            "message": (
                "Only one model version is currently "
                "registered. It is being established "
                "as the performance baseline."
            ),
        },
        "metrics": {
            "classification": {},
            "regression": {},
        },
    }

    return report


def create_comparison_report(
    registry: Dict[str, Any],
    retraining_report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare the current model with a candidate model.

    If the retraining report does not contain candidate
    metrics, the current model remains the baseline.
    """

    current_version = get_current_version(registry)

    latest_version = get_latest_version(registry)

    if latest_version is None:
        raise ValueError(
            "No registered model version found."
        )

    candidate_version = latest_version.get(
        "version",
        "UNKNOWN",
    )

    retraining_required = retraining_report.get(
        "retraining_required",
        False,
    )

    retraining_performed = retraining_report.get(
        "retraining_performed",
        False,
    )

    if not retraining_required or not retraining_performed:
        return create_baseline_report(registry)

    candidate_metrics = extract_metrics(
        retraining_report
    )

    baseline_metrics = retraining_report.get(
        "previous_model_metrics",
        {},
    )

    if not baseline_metrics:
        baseline_metrics = {}

    comparisons = {}

    metric_directions = {
        "accuracy_percent": True,
        "precision_percent": True,
        "recall_percent": True,
        "f1_percent": True,
        "roc_auc_percent": True,
        "mae_days": False,
        "rmse_days": False,
        "r2": True,
    }

    for metric, higher_is_better in metric_directions.items():

        current_value = baseline_metrics.get(metric)

        candidate_value = candidate_metrics.get(metric)

        comparisons[metric] = compare_metric(
            current_value,
            candidate_value,
            higher_is_better,
        )

    score = calculate_comparison_score(
        comparisons
    )

    candidate_is_better = (
        score["overall_result"] == "IMPROVED"
    )

    recommendation = (
        "PROMOTE_CANDIDATE"
        if candidate_is_better
        else "KEEP_CURRENT_MODEL"
    )

    return {
        "system": "SupplyPrescript",
        "module": "AI Model Performance Comparison Engine",
        "generated_at": get_timestamp(),
        "comparison_type": "MODEL_COMPARISON",
        "current_version": current_version,
        "candidate_version": candidate_version,
        "decision": {
            "candidate_is_better": candidate_is_better,
            "recommendation": recommendation,
        },
        "summary": score,
        "metrics": {
            "baseline": baseline_metrics,
            "candidate": candidate_metrics,
            "comparison": comparisons,
        },
    }


def print_report(
    report: Dict[str, Any]
) -> None:
    """Display the comparison report."""

    print()
    print("=" * 90)
    print("SUPPLYPRESCRIPT - MODEL PERFORMANCE COMPARISON")
    print("=" * 90)

    print()
    print(
        f"Current Version:   "
        f"{report.get('current_version')}"
    )

    print(
        f"Candidate Version: "
        f"{report.get('candidate_version')}"
    )

    print(
        f"Comparison Type:   "
        f"{report.get('comparison_type')}"
    )

    summary = report.get("summary", {})

    print()
    print("Comparison Status:")

    if summary.get("status"):
        print(
            f"   {summary.get('status')}"
        )

    if summary.get("overall_result"):
        print(
            f"   Overall Result: "
            f"{summary.get('overall_result')}"
        )

    print()
    print("Decision:")

    decision = report.get("decision", {})

    print(
        f"   Candidate Better: "
        f"{decision.get('candidate_is_better')}"
    )

    print(
        f"   Recommendation: "
        f"{decision.get('recommendation')}"
    )

    if "improved_metrics" in summary:
        print()
        print("Metric Comparison:")
        print(
            f"   Improved:     "
            f"{summary.get('improved_metrics')}"
        )
        print(
            f"   Declined:     "
            f"{summary.get('declined_metrics')}"
        )
        print(
            f"   Unchanged:    "
            f"{summary.get('unchanged_metrics')}"
        )
        print(
            f"   Not Available:"
            f" {summary.get('unavailable_metrics')}"
        )

    print()
    print("=" * 90)


def main() -> None:
    """Run the model performance comparison engine."""

    print()
    print("Loading model version registry...")

    registry = load_json(
        VERSION_REGISTRY_FILE
    )

    print(
        f"   ✓ Current version: "
        f"{registry.get('current_version')}"
    )

    print()
    print("Loading retraining report...")

    if RETRAINING_REPORT_FILE.exists():
        retraining_report = load_json(
            RETRAINING_REPORT_FILE
        )

        print(
            "   ✓ Retraining report loaded."
        )
    else:
        retraining_report = {
            "retraining_required": False,
            "retraining_performed": False,
        }

        print(
            "   ⚠ No retraining report found."
        )
        print(
            "   Using baseline comparison mode."
        )

    report = create_comparison_report(
        registry,
        retraining_report,
    )

    save_json(
        COMPARISON_REPORT_FILE,
        report,
    )

    print_report(report)

    print()
    print("✓ Comparison report saved:")
    print(
        f"  {COMPARISON_REPORT_FILE}"
    )

    print()
    print(
        "MODEL PERFORMANCE COMPARISON "
        "ENGINE COMPLETED"
    )


if __name__ == "__main__":
    main()