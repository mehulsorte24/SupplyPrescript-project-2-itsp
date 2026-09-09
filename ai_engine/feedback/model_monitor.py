from pathlib import Path
import json
from datetime import datetime, timezone


PROJECT_ROOT = Path.cwd()

FEEDBACK_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "prediction_outcomes.json"
)

ERROR_ANALYSIS_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "error_analysis.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "model_monitoring_report.json"
)


# Monitoring thresholds
MIN_ACCURACY_PERCENT = 75.0
MAX_MEAN_DELAY_ERROR_DAYS = 2.0
MAX_MISSED_DELAY_RATE_PERCENT = 20.0
MAX_FALSE_ALERT_RATE_PERCENT = 20.0


def load_json(file_path):
    """Load a JSON file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def calculate_monitoring_metrics(
    feedback,
    error_analysis,
):
    """Calculate model monitoring metrics."""

    summary = feedback.get(
        "summary",
        {}
    )

    statistics = error_analysis.get(
        "overall_statistics",
        {}
    )

    total_evaluated = int(
        summary.get(
            "evaluated_records",
            statistics.get(
                "total_evaluated",
                0
            ),
        )
    )

    correct_predictions = int(
        summary.get(
            "correct_predictions",
            statistics.get(
                "correct_predictions",
                0
            ),
        )
    )

    incorrect_predictions = int(
        summary.get(
            "incorrect_predictions",
            statistics.get(
                "incorrect_predictions",
                0
            ),
        )
    )

    accuracy = float(
        summary.get(
            "classification_accuracy_percent",
            statistics.get(
                "classification_accuracy_percent",
                0.0
            ),
        )
    )

    mean_delay_error = float(
        summary.get(
            "mean_absolute_delay_error_days",
            statistics.get(
                "mean_absolute_delay_error_days",
                0.0
            ),
        )
    )

    missed_delays = int(
        statistics.get(
            "missed_delays",
            0
        )
    )

    false_alerts = int(
        statistics.get(
            "false_delay_alerts",
            0
        )
    )

    if total_evaluated > 0:
        missed_delay_rate = (
            missed_delays
            / total_evaluated
        ) * 100

        false_alert_rate = (
            false_alerts
            / total_evaluated
        ) * 100
    else:
        missed_delay_rate = 0.0
        false_alert_rate = 0.0

    return {
        "total_evaluated": total_evaluated,
        "correct_predictions": correct_predictions,
        "incorrect_predictions": incorrect_predictions,
        "classification_accuracy_percent": round(
            accuracy,
            2,
        ),
        "mean_absolute_delay_error_days": round(
            mean_delay_error,
            4,
        ),
        "missed_delays": missed_delays,
        "missed_delay_rate_percent": round(
            missed_delay_rate,
            2,
        ),
        "false_delay_alerts": false_alerts,
        "false_delay_alert_rate_percent": round(
            false_alert_rate,
            2,
        ),
    }


def evaluate_metric(
    metric_name,
    value,
    threshold,
    condition,
):
    """Evaluate an individual monitoring metric."""

    if condition == "minimum":
        passed = value >= threshold
    else:
        passed = value <= threshold

    return {
        "metric": metric_name,
        "value": round(
            float(value),
            4,
        ),
        "threshold": threshold,
        "condition": (
            "greater_than_or_equal"
            if condition == "minimum"
            else "less_than_or_equal"
        ),
        "status": (
            "PASS"
            if passed
            else "WARNING"
        ),
    }


def determine_model_status(metric_checks):
    """Determine overall model health."""

    warning_count = sum(
        1
        for check in metric_checks
        if check["status"] == "WARNING"
    )

    if warning_count == 0:
        return "HEALTHY"

    if warning_count == 1:
        return "MONITOR"

    return "RETRAIN_RECOMMENDED"


def generate_monitoring_recommendations(
    model_status,
    metric_checks,
):
    """Generate monitoring recommendations."""

    recommendations = []

    if model_status == "HEALTHY":
        recommendations.append(
            "Model performance is within all configured "
            "monitoring thresholds."
        )

    elif model_status == "MONITOR":
        recommendations.append(
            "One monitoring metric exceeded its threshold; "
            "continue monitoring future prediction outcomes."
        )

    else:
        recommendations.append(
            "Multiple monitoring metrics exceeded their "
            "thresholds; model retraining is recommended."
        )

    for check in metric_checks:
        if check["status"] == "WARNING":

            if check["metric"] == "classification_accuracy":
                recommendations.append(
                    "Classification accuracy is below the "
                    "minimum acceptable threshold."
                )

            elif check["metric"] == "delay_prediction_error":
                recommendations.append(
                    "Average delay prediction error is above "
                    "the configured limit."
                )

            elif check["metric"] == "missed_delay_rate":
                recommendations.append(
                    "The missed-delay rate is above the "
                    "configured limit; investigate false negatives."
                )

            elif check["metric"] == "false_delay_alert_rate":
                recommendations.append(
                    "The false-delay alert rate is above the "
                    "configured limit; investigate false positives."
                )

    recommendations.append(
        "Continue collecting actual shipment outcomes "
        "to improve monitoring reliability."
    )

    return recommendations


def build_monitoring_report(
    feedback,
    error_analysis,
):
    """Build the complete model monitoring report."""

    metrics = calculate_monitoring_metrics(
        feedback,
        error_analysis,
    )

    metric_checks = [
        evaluate_metric(
            "classification_accuracy",
            metrics[
                "classification_accuracy_percent"
            ],
            MIN_ACCURACY_PERCENT,
            "minimum",
        ),
        evaluate_metric(
            "delay_prediction_error",
            metrics[
                "mean_absolute_delay_error_days"
            ],
            MAX_MEAN_DELAY_ERROR_DAYS,
            "maximum",
        ),
        evaluate_metric(
            "missed_delay_rate",
            metrics[
                "missed_delay_rate_percent"
            ],
            MAX_MISSED_DELAY_RATE_PERCENT,
            "maximum",
        ),
        evaluate_metric(
            "false_delay_alert_rate",
            metrics[
                "false_delay_alert_rate_percent"
            ],
            MAX_FALSE_ALERT_RATE_PERCENT,
            "maximum",
        ),
    ]

    model_status = determine_model_status(
        metric_checks
    )

    recommendations = (
        generate_monitoring_recommendations(
            model_status,
            metric_checks,
        )
    )

    return {
        "system": "SupplyPrescript",
        "module": "AI Model Monitoring Engine",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "monitoring_status": model_status,
        "monitoring_metrics": metrics,
        "metric_checks": metric_checks,
        "thresholds": {
            "minimum_accuracy_percent": (
                MIN_ACCURACY_PERCENT
            ),
            "maximum_mean_delay_error_days": (
                MAX_MEAN_DELAY_ERROR_DAYS
            ),
            "maximum_missed_delay_rate_percent": (
                MAX_MISSED_DELAY_RATE_PERCENT
            ),
            "maximum_false_delay_alert_rate_percent": (
                MAX_FALSE_ALERT_RATE_PERCENT
            ),
        },
        "recommendations": recommendations,
    }


def save_report(report):
    """Save monitoring report."""

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


def run_model_monitoring():
    """Run the complete AI model monitoring engine."""

    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI MODEL MONITORING ENGINE"
    )
    print("=" * 100)

    print("\nLoading prediction feedback...")

    feedback = load_json(
        FEEDBACK_FILE
    )

    print(
        "   ✓ Prediction feedback loaded."
    )

    print("\nLoading error analysis...")

    error_analysis = load_json(
        ERROR_ANALYSIS_FILE
    )

    print(
        "   ✓ Error analysis loaded."
    )

    print("\nCalculating monitoring metrics...")

    report = build_monitoring_report(
        feedback,
        error_analysis,
    )

    metrics = report[
        "monitoring_metrics"
    ]

    print(
        f"   ✓ Evaluated records: "
        f"{metrics['total_evaluated']}"
    )

    print("\nMODEL MONITORING SUMMARY")
    print("=" * 100)

    print(
        f"Classification accuracy     : "
        f"{metrics['classification_accuracy_percent']:.2f}%"
    )

    print(
        f"Mean delay prediction error : "
        f"{metrics['mean_absolute_delay_error_days']:.2f} days"
    )

    print(
        f"Missed-delay rate           : "
        f"{metrics['missed_delay_rate_percent']:.2f}%"
    )

    print(
        f"False-alert rate            : "
        f"{metrics['false_delay_alert_rate_percent']:.2f}%"
    )

    print("\nMetric Checks:")

    for check in report[
        "metric_checks"
    ]:
        print(
            f"   {check['metric']}: "
            f"{check['status']}"
        )

    print(
        f"\nOverall Model Status        : "
        f"{report['monitoring_status']}"
    )

    print("\nRecommendations:")

    for recommendation in report[
        "recommendations"
    ]:
        print(
            f"   • {recommendation}"
        )

    save_report(report)

    print(
        f"\n✓ Monitoring report saved:\n"
        f"  {OUTPUT_FILE}"
    )

    print("\n" + "=" * 100)
    print(
        "AI MODEL MONITORING ENGINE COMPLETED"
    )
    print("=" * 100)

    return report


if __name__ == "__main__":
    run_model_monitoring()
