from pathlib import Path
import json
from datetime import datetime, timezone


PROJECT_ROOT = Path.cwd()

MONITORING_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "model_monitoring_report.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_trigger.json"
)


RETRAINING_STATUSES = {
    "RETRAIN_RECOMMENDED",
}


def load_monitoring_report():
    """Load the latest AI model monitoring report."""

    if not MONITORING_FILE.exists():
        raise FileNotFoundError(
            f"Monitoring report not found: {MONITORING_FILE}"
        )

    with open(
        MONITORING_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def evaluate_retraining_need(report):
    """Determine whether model retraining should be triggered."""

    monitoring_status = report.get(
        "monitoring_status",
        "UNKNOWN",
    )

    metric_checks = report.get(
        "metric_checks",
        [],
    )

    warning_metrics = [
        check
        for check in metric_checks
        if check.get("status") == "WARNING"
    ]

    retraining_required = (
        monitoring_status in RETRAINING_STATUSES
        or len(warning_metrics) >= 2
    )

    if retraining_required:
        trigger_status = "RETRAIN_REQUIRED"
        action = (
            "Trigger model retraining pipeline."
        )
    elif monitoring_status == "MONITOR":
        trigger_status = "MONITOR"
        action = (
            "Continue monitoring model performance "
            "before retraining."
        )
    elif monitoring_status == "HEALTHY":
        trigger_status = "NO_RETRAINING_REQUIRED"
        action = (
            "Continue using the current model "
            "and collect additional outcomes."
        )
    else:
        trigger_status = "REVIEW_REQUIRED"
        action = (
            "Review model monitoring results manually "
            "before taking retraining action."
        )

    return {
        "monitoring_status": monitoring_status,
        "warning_metric_count": len(
            warning_metrics
        ),
        "warning_metrics": [
            check.get("metric")
            for check in warning_metrics
        ],
        "retraining_required": retraining_required,
        "trigger_status": trigger_status,
        "recommended_action": action,
    }


def build_trigger_report(report):
    """Build the complete retraining trigger report."""

    decision = evaluate_retraining_need(
        report
    )

    return {
        "system": "SupplyPrescript",
        "module": "Automated Retraining Trigger Engine",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_monitoring_status": report.get(
            "monitoring_status",
            "UNKNOWN",
        ),
        "decision": decision,
    }


def save_trigger_report(trigger_report):
    """Save retraining trigger decision."""

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
            trigger_report,
            file,
            indent=4,
        )


def run_retraining_trigger():
    """Run the automated retraining trigger engine."""

    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AUTOMATED RETRAINING TRIGGER ENGINE"
    )
    print("=" * 100)

    print("\nLoading model monitoring report...")

    report = load_monitoring_report()

    print(
        "   ✓ Monitoring report loaded."
    )

    print("\nEvaluating retraining conditions...")

    trigger_report = build_trigger_report(
        report
    )

    decision = trigger_report[
        "decision"
    ]

    print(
        f"   ✓ Monitoring status: "
        f"{decision['monitoring_status']}"
    )

    print(
        f"   ✓ Warning metrics: "
        f"{decision['warning_metric_count']}"
    )

    print("\nRETRAINING DECISION")
    print("=" * 100)

    print(
        f"Monitoring status       : "
        f"{decision['monitoring_status']}"
    )

    print(
        f"Warning metrics         : "
        f"{decision['warning_metric_count']}"
    )

    print(
        f"Retraining required     : "
        f"{decision['retraining_required']}"
    )

    print(
        f"Trigger status          : "
        f"{decision['trigger_status']}"
    )

    print(
        f"Recommended action      : "
        f"{decision['recommended_action']}"
    )

    if decision["warning_metrics"]:
        print(
            "\nWarning metrics:"
        )

        for metric in decision[
            "warning_metrics"
        ]:
            print(
                f"   • {metric}"
            )

    save_trigger_report(
        trigger_report
    )

    print(
        f"\n✓ Retraining trigger report saved:\n"
        f"  {OUTPUT_FILE}"
    )

    print("\n" + "=" * 100)
    print(
        "AUTOMATED RETRAINING TRIGGER ENGINE COMPLETED"
    )
    print("=" * 100)

    return trigger_report


if __name__ == "__main__":
    run_retraining_trigger()
