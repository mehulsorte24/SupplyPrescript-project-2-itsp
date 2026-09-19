import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path.cwd() / "ai_engine" / "prediction"

HISTORY_FILE = BASE_DIR / "escalation_history.json"
OUTPUT_FILE = BASE_DIR / "escalation_trend_intelligence_report.json"

ENGINE_NAME = "AI Escalation Trend Intelligence Engine"
ENGINE_VERSION = "1.0"


def load_history():
    print("Searching for AI escalation history...")

    if not HISTORY_FILE.exists():
        print("Escalation history file not found:")
        print(HISTORY_FILE)
        return None

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        print("AI escalation history loaded.")
        return data

    except json.JSONDecodeError as error:
        print("Invalid JSON in escalation history.")
        print(error)
        return None

    except OSError as error:
        print("Could not read escalation history.")
        print(error)
        return None


def get_records(data):
    if not isinstance(data, dict):
        return []

    records = data.get("records", [])

    if not isinstance(records, list):
        return []

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def parse_datetime(value):
    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def sort_records(records):
    sortable = []

    for record in records:
        timestamp = parse_datetime(
            record.get("captured_at")
        )

        if timestamp is not None:
            sortable.append(
                (timestamp, record)
            )

    sortable.sort(
        key=lambda item: item[0]
    )

    return [
        item[1]
        for item in sortable
    ]


def analyze_metric(records, field, name):
    if len(records) < 2:
        current_value = 0.0

        if len(records) == 1:
            current_value = safe_float(
                records[0].get(field)
            )

        return {
            "metric": name,
            "field": field,
            "status": "INSUFFICIENT_HISTORY",
            "current_value": current_value,
            "previous_value": None,
            "change": None,
            "direction": "UNKNOWN",
            "severity": "UNKNOWN"
        }

    previous_value = safe_float(
        records[-2].get(field)
    )

    current_value = safe_float(
        records[-1].get(field)
    )

    change = round(
        current_value - previous_value,
        4
    )

    if change > 0.01:
        direction = "INCREASING"
    elif change < -0.01:
        direction = "DECREASING"
    else:
        direction = "STABLE"

    absolute_change = abs(change)

    if absolute_change >= 20:
        severity = "STRONG"
    elif absolute_change >= 10:
        severity = "MODERATE"
    elif absolute_change > 0.01:
        severity = "MILD"
    else:
        severity = "STABLE"

    return {
        "metric": name,
        "field": field,
        "status": "AVAILABLE",
        "current_value": current_value,
        "previous_value": previous_value,
        "change": change,
        "direction": direction,
        "severity": severity
    }


def analyze_all_metrics(records):
    definitions = [
        ("risk_exposure_score", "Risk Exposure"),
        ("escalation_score", "Escalation Score"),
        ("delayed_percentage", "Delayed Percentage"),
        ("critical_percentage", "Critical Percentage"),
        ("high_critical_percentage", "High/Critical Percentage"),
        ("delay_probability", "Delay Probability"),
        ("expected_delay_days", "Expected Delay Days"),
        ("confidence", "AI Confidence"),
        ("intelligence", "AI Intelligence")
    ]

    results = {}

    for field, name in definitions:
        results[field] = analyze_metric(
            records,
            field,
            name
        )

    return results


def analyze_overall_trend(metrics):
    available = [
        metric
        for metric in metrics.values()
        if metric["status"] == "AVAILABLE"
    ]

    if not available:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "direction": "UNKNOWN",
            "severity": "UNKNOWN",
            "confidence": "LOW",
            "increasing_metrics": 0,
            "decreasing_metrics": 0,
            "stable_metrics": 0
        }

    increasing = sum(
        metric["direction"] == "INCREASING"
        for metric in available
    )

    decreasing = sum(
        metric["direction"] == "DECREASING"
        for metric in available
    )

    stable = sum(
        metric["direction"] == "STABLE"
        for metric in available
    )

    if increasing > decreasing:
        direction = "INCREASING"
    elif decreasing > increasing:
        direction = "DECREASING"
    else:
        direction = "STABLE"

    if any(
        metric["severity"] == "STRONG"
        for metric in available
    ):
        severity = "STRONG"
    elif any(
        metric["severity"] == "MODERATE"
        for metric in available
    ):
        severity = "MODERATE"
    else:
        severity = "MILD"

    if len(available) >= 7:
        confidence = "HIGH"
    elif len(available) >= 4:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "status": "AVAILABLE",
        "direction": direction,
        "severity": severity,
        "confidence": confidence,
        "increasing_metrics": increasing,
        "decreasing_metrics": decreasing,
        "stable_metrics": stable
    }


def analyze_risk_trend(metrics):
    risk_fields = [
        "risk_exposure_score",
        "escalation_score",
        "delayed_percentage",
        "critical_percentage",
        "high_critical_percentage",
        "delay_probability",
        "expected_delay_days"
    ]

    available = [
        metrics[field]
        for field in risk_fields
        if metrics[field]["status"] == "AVAILABLE"
    ]

    if not available:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "direction": "UNKNOWN",
            "severity": "UNKNOWN",
            "increasing_metrics": 0,
            "decreasing_metrics": 0,
            "stable_metrics": 0
        }

    increasing = sum(
        metric["direction"] == "INCREASING"
        for metric in available
    )

    decreasing = sum(
        metric["direction"] == "DECREASING"
        for metric in available
    )

    stable = sum(
        metric["direction"] == "STABLE"
        for metric in available
    )

    if increasing > decreasing:
        direction = "INCREASING"
    elif decreasing > increasing:
        direction = "DECREASING"
    else:
        direction = "STABLE"

    if any(
        metric["severity"] == "STRONG"
        for metric in available
        if metric["direction"] == "INCREASING"
    ):
        severity = "STRONG"
    elif any(
        metric["severity"] == "MODERATE"
        for metric in available
        if metric["direction"] == "INCREASING"
    ):
        severity = "MODERATE"
    elif increasing > 0:
        severity = "MILD"
    else:
        severity = "STABLE"

    return {
        "status": "AVAILABLE",
        "direction": direction,
        "severity": severity,
        "increasing_metrics": increasing,
        "decreasing_metrics": decreasing,
        "stable_metrics": stable
    }


def analyze_ai_quality(metrics):
    confidence = metrics["confidence"]
    intelligence = metrics["intelligence"]

    if (
        confidence["status"] != "AVAILABLE"
        or intelligence["status"] != "AVAILABLE"
    ):
        return {
            "status": "INSUFFICIENT_HISTORY",
            "direction": "UNKNOWN",
            "confidence_direction": "UNKNOWN",
            "intelligence_direction": "UNKNOWN"
        }

    confidence_direction = confidence["direction"]
    intelligence_direction = intelligence["direction"]

    if (
        confidence_direction == "DECREASING"
        or intelligence_direction == "DECREASING"
    ):
        direction = "DEGRADING"

    elif (
        confidence_direction == "INCREASING"
        and intelligence_direction == "INCREASING"
    ):
        direction = "IMPROVING"

    else:
        direction = "STABLE"

    return {
        "status": "AVAILABLE",
        "direction": direction,
        "confidence_direction": confidence_direction,
        "intelligence_direction": intelligence_direction
    }


def generate_signals(
    records,
    metrics,
    overall,
    risk,
    quality
):
    signals = []

    if len(records) < 2:
        signals.append(
            "At least two escalation records are required to establish a temporal trend."
        )

        signals.append(
            "The current record represents a baseline rather than a confirmed trend."
        )

        return signals

    if risk["direction"] == "INCREASING":
        signals.append(
            "Operational risk indicators are trending upward."
        )
    elif risk["direction"] == "DECREASING":
        signals.append(
            "Operational risk indicators are trending downward."
        )
    else:
        signals.append(
            "Operational risk indicators are currently stable."
        )

    if quality["direction"] == "DEGRADING":
        signals.append(
            "AI confidence or intelligence indicators are trending downward."
        )
    elif quality["direction"] == "IMPROVING":
        signals.append(
            "AI confidence and intelligence indicators are trending upward."
        )
    else:
        signals.append(
            "AI quality indicators show no dominant directional change."
        )

    if (
        metrics["critical_percentage"]["status"] == "AVAILABLE"
        and metrics["critical_percentage"]["direction"] == "INCREASING"
    ):
        signals.append(
            "Critical-risk prediction percentage is increasing."
        )

    if (
        metrics["delayed_percentage"]["status"] == "AVAILABLE"
        and metrics["delayed_percentage"]["direction"] == "INCREASING"
    ):
        signals.append(
            "Delayed prediction percentage is increasing."
        )

    if (
        metrics["risk_exposure_score"]["status"] == "AVAILABLE"
        and metrics["risk_exposure_score"]["direction"] == "INCREASING"
    ):
        signals.append(
            "Risk exposure score is increasing."
        )

    if (
        metrics["escalation_score"]["status"] == "AVAILABLE"
        and metrics["escalation_score"]["direction"] == "INCREASING"
    ):
        signals.append(
            "Escalation score is increasing."
        )

    if overall["direction"] == "INCREASING":
        signals.append(
            "The majority of analyzed metrics are moving upward."
        )

    return signals


def determine_intelligence(
    records,
    risk,
    quality
):
    if len(records) < 2:
        return {
            "level": "BASELINE",
            "status": "INSUFFICIENT_HISTORY",
            "confidence": "LOW"
        }

    if (
        risk["direction"] == "INCREASING"
        and risk["severity"] in [
            "STRONG",
            "MODERATE"
        ]
    ):
        return {
            "level": "ESCALATING_RISK",
            "status": "RISK_TREND_INCREASING",
            "confidence": "MEDIUM"
        }

    if risk["direction"] == "DECREASING":
        return {
            "level": "IMPROVING_RISK",
            "status": "RISK_TREND_DECREASING",
            "confidence": "MEDIUM"
        }

    if quality["direction"] == "DEGRADING":
        return {
            "level": "AI_QUALITY_WARNING",
            "status": "AI_QUALITY_DEGRADING",
            "confidence": "MEDIUM"
        }

    return {
        "level": "STABLE",
        "status": "NO_DOMINANT_TREND",
        "confidence": "MEDIUM"
    }


def get_recommendation(
    intelligence,
    record_count
):
    if record_count < 2:
        return (
            "Continue collecting escalation history. "
            "Additional records are required before confirming an operational trend."
        )

    if intelligence["level"] == "ESCALATING_RISK":
        return (
            "Increase operational monitoring and review recurring "
            "risk drivers before executing high-impact supply decisions."
        )

    if intelligence["level"] == "IMPROVING_RISK":
        return (
            "Continue monitoring the improving risk trend while "
            "validating that the improvement persists."
        )

    if intelligence["level"] == "AI_QUALITY_WARNING":
        return (
            "Review AI confidence and intelligence trends and evaluate "
            "whether additional model monitoring or retraining analysis is required."
        )

    return (
        "Continue standard operational monitoring while accumulating "
        "additional escalation history."
    )


def build_report(
    records,
    metrics,
    overall,
    risk,
    quality,
    signals,
    intelligence
):
    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "status": "COMPLETED",
        "analyzed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "records_analyzed": len(records),
        "metric_trends": metrics,
        "overall_trend": overall,
        "risk_trend": risk,
        "ai_quality_trend": quality,
        "trend_signals": signals,
        "trend_intelligence": intelligence,
        "operational_recommendation": get_recommendation(
            intelligence,
            len(records)
        ),
        "operational_safety": {
            "escalation_history_modified": False,
            "prediction_outputs_modified": False,
            "risk_reports_modified": False,
            "models_modified": False,
            "retraining_triggered": False,
            "optimization_modified": False,
            "database_modified": False
        }
    }


def save_report(report):
    try:
        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=2
            )

        return True

    except OSError as error:
        print("Failed to save report.")
        print(error)
        return False


def print_summary(
    records,
    metrics,
    overall,
    risk,
    quality,
    signals,
    intelligence
):
    print()
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI ESCALATION TREND INTELLIGENCE ENGINE"
    )
    print("=" * 90)

    print()
    print("HISTORY OVERVIEW")
    print("-" * 90)
    print(
        f"Records Analyzed: {len(records)}"
    )

    print()
    print("METRIC TRENDS")
    print("-" * 90)

    for field, metric in metrics.items():
        print(
            f"{metric['metric']}: "
            f"{metric['direction']}"
        )

    print()
    print("OVERALL TREND")
    print("-" * 90)
    print(
        f"Direction: {overall['direction']}"
    )
    print(
        f"Severity: {overall['severity']}"
    )
    print(
        f"Confidence: {overall['confidence']}"
    )

    print()
    print("RISK TREND")
    print("-" * 90)
    print(
        f"Direction: {risk['direction']}"
    )
    print(
        f"Severity: {risk['severity']}"
    )

    print()
    print("AI QUALITY TREND")
    print("-" * 90)
    print(
        f"Direction: {quality['direction']}"
    )
    print(
        f"Confidence Direction: {quality['confidence_direction']}"
    )
    print(
        f"Intelligence Direction: {quality['intelligence_direction']}"
    )

    print()
    print("TREND SIGNALS")
    print("-" * 90)

    for number, signal in enumerate(
        signals,
        start=1
    ):
        print(
            f"{number:02d}. {signal}"
        )

    print()
    print("TREND INTELLIGENCE")
    print("-" * 90)
    print(
        f"Level: {intelligence['level']}"
    )
    print(
        f"Status: {intelligence['status']}"
    )
    print(
        f"Confidence: {intelligence['confidence']}"
    )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)
    print("Escalation history modified: NO")
    print("Prediction outputs modified: NO")
    print("Risk reports modified: NO")
    print("Models modified: NO")
    print("Retraining triggered: NO")
    print("Optimization modified: NO")
    print("Database modified: NO")

    print()
    print("=" * 90)
    print(
        "AI escalation trend intelligence analysis completed successfully."
    )
    print(
        f"Report saved: {OUTPUT_FILE}"
    )
    print("=" * 90)


def main():
    data = load_history()

    if data is None:
        return

    print()
    print("Extracting escalation history records...")

    records = get_records(data)
    records = sort_records(records)

    print(
        f"Records extracted: {len(records)}"
    )

    print()
    print("Calculating metric trends...")

    metrics = analyze_all_metrics(
        records
    )

    print(
        "Metric trend analysis completed."
    )

    print()
    print("Calculating overall trend...")

    overall = analyze_overall_trend(
        metrics
    )

    print(
        "Overall trend calculated."
    )

    print()
    print("Analyzing risk trend...")

    risk = analyze_risk_trend(
        metrics
    )

    print(
        "Risk trend analysis completed."
    )

    print()
    print("Analyzing AI quality trend...")

    quality = analyze_ai_quality(
        metrics
    )

    print(
        "AI quality trend analysis completed."
    )

    print()
    print("Generating trend signals...")

    signals = generate_signals(
        records,
        metrics,
        overall,
        risk,
        quality
    )

    print(
        f"Trend signals generated: {len(signals)}"
    )

    print()
    print("Determining trend intelligence...")

    intelligence = determine_intelligence(
        records,
        risk,
        quality
    )

    print(
        f"Intelligence level: {intelligence['level']}"
    )

    report = build_report(
        records,
        metrics,
        overall,
        risk,
        quality,
        signals,
        intelligence
    )

    print()
    print("Saving trend intelligence report...")

    if not save_report(report):
        return

    print(
        "Trend intelligence report saved."
    )

    print_summary(
        records,
        metrics,
        overall,
        risk,
        quality,
        signals,
        intelligence
    )


if __name__ == "__main__":
    main()