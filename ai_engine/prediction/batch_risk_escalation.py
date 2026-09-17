import json
from pathlib import Path
from statistics import mean


BASE_DIR = Path(__file__).resolve().parent

RISK_REPORT_FILE = BASE_DIR / "batch_risk_aggregation_report.json"
HISTORY_FILE = BASE_DIR / "batch_quality_history.json"
OUTPUT_FILE = BASE_DIR / "batch_risk_escalation_report.json"


MONITOR_NAME = "AI Batch Risk Trend & Escalation Engine"
MONITOR_VERSION = "1.2"


def load_json_file(file_path: Path, description: str):
    print(f"Searching for {description}...")

    if not file_path.exists():
        print("   ✗ File not found:")
        print(f"     {file_path}")
        return None

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        print(f"   ✓ {description.capitalize()} loaded.")
        print(f"     {file_path}")
        return data

    except json.JSONDecodeError as exc:
        print(f"   ✗ Failed to parse {description}:")
        print(f"     {exc}")
        return None

    except OSError as exc:
        print(f"   ✗ Failed to read {description}:")
        print(f"     {exc}")
        return None


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_level(level):
    if not isinstance(level, str):
        return "UNKNOWN"

    return level.strip().upper()


def extract_current_risk_metrics(risk_report):
    """
    Extract metrics from the flat structure produced by
    batch_risk_aggregation.py.
    """

    prediction_distribution = risk_report.get(
        "prediction_distribution",
        {}
    )

    risk_distribution = risk_report.get(
        "risk_distribution",
        {}
    )

    average_metrics = risk_report.get(
        "average_metrics",
        {}
    )

    batch_risk = risk_report.get(
        "batch_risk",
        {}
    )

    return {
        "total_predictions": safe_int(
            risk_report.get("total_predictions")
        ),
        "on_time": safe_int(
            prediction_distribution.get("ON_TIME")
        ),
        "delayed": safe_int(
            prediction_distribution.get("DELAYED")
        ),
        "delayed_percentage": safe_float(
            prediction_distribution.get("DELAYED_PERCENTAGE")
        ),
        "low": safe_int(
            risk_distribution.get("LOW")
        ),
        "medium": safe_int(
            risk_distribution.get("MEDIUM")
        ),
        "high": safe_int(
            risk_distribution.get("HIGH")
        ),
        "critical": safe_int(
            risk_distribution.get("CRITICAL")
        ),
        "high_critical_percentage": safe_float(
            risk_distribution.get("HIGH_OR_CRITICAL_PERCENTAGE")
        ),
        "critical_percentage": safe_float(
            risk_distribution.get("CRITICAL_PERCENTAGE")
        ),
        "delay_probability": safe_float(
            average_metrics.get("delay_probability")
        ),
        "expected_delay_days": safe_float(
            average_metrics.get("expected_delay_days")
        ),
        "confidence": safe_float(
            average_metrics.get("confidence")
        ),
        "intelligence": safe_float(
            average_metrics.get("intelligence")
        ),
        "risk_exposure_score": safe_float(
            batch_risk.get("risk_exposure_score")
        ),
        "overall_risk_level": normalize_level(
            batch_risk.get("overall_risk_level")
        ),
    }


def extract_history_batches(history_data):
    """
    Extract historical batches from batch_quality_history.json.
    """

    if not isinstance(history_data, dict):
        return []

    batches = history_data.get("batches", [])

    if not isinstance(batches, list):
        return []

    return [
        batch
        for batch in batches
        if isinstance(batch, dict)
    ]


def extract_history_metrics(batch):
    """
    Extract metrics directly from the flat historical batch
    structure produced by batch_quality_history.py.
    """

    return {
        "batch_number": safe_int(
            batch.get("batch_number")
        ),
        "predictions": safe_int(
            batch.get("total_predictions")
        ),
        "valid_predictions": safe_int(
            batch.get("valid_predictions")
        ),
        "invalid_predictions": safe_int(
            batch.get("invalid_predictions")
        ),
        "quality_score": safe_float(
            batch.get("batch_quality_score")
        ),
        "validation_score": safe_float(
            batch.get("validation_score")
        ),
        "confidence": safe_float(
            batch.get("average_confidence_score")
        ),
        "intelligence": safe_float(
            batch.get("average_intelligence_score")
        ),
        "delayed_predictions": safe_int(
            batch.get("delayed_predictions")
        ),
        "critical_predictions": safe_int(
            batch.get("critical_predictions")
        ),
        "delayed_percentage": safe_float(
            batch.get("delayed_percentage")
        ),
    }


def calculate_historical_baseline(history_batches):
    extracted = []

    for batch in history_batches:
        metrics = extract_history_metrics(batch)

        if metrics["predictions"] > 0:
            extracted.append(metrics)

    if not extracted:
        return {
            "available": False,
            "batch_count": 0,
            "average_predictions": 0.0,
            "average_quality_score": 0.0,
            "average_validation_score": 0.0,
            "average_confidence": 0.0,
            "average_intelligence": 0.0,
            "average_delayed_predictions": 0.0,
            "average_delayed_percentage": 0.0,
            "average_critical_predictions": 0.0,
            "average_critical_percentage": 0.0,
        }

    average_predictions = mean(
        item["predictions"]
        for item in extracted
    )

    average_delayed_predictions = mean(
        item["delayed_predictions"]
        for item in extracted
    )

    average_critical_predictions = mean(
        item["critical_predictions"]
        for item in extracted
    )

    if average_predictions > 0:
        average_critical_percentage = (
            average_critical_predictions
            / average_predictions
        ) * 100.0
    else:
        average_critical_percentage = 0.0

    return {
        "available": True,
        "batch_count": len(extracted),
        "average_predictions": average_predictions,
        "average_quality_score": mean(
            item["quality_score"]
            for item in extracted
        ),
        "average_validation_score": mean(
            item["validation_score"]
            for item in extracted
        ),
        "average_confidence": mean(
            item["confidence"]
            for item in extracted
        ),
        "average_intelligence": mean(
            item["intelligence"]
            for item in extracted
        ),
        "average_delayed_predictions": average_delayed_predictions,
        "average_delayed_percentage": mean(
            item["delayed_percentage"]
            for item in extracted
        ),
        "average_critical_predictions": average_critical_predictions,
        "average_critical_percentage": average_critical_percentage,
    }


def calculate_change(current, baseline):
    return round(
        current - baseline,
        4
    )


def determine_risk_trend(current, baseline):
    """
    Establish risk trend only when enough historical batches exist.

    One historical batch is treated as a baseline rather than
    evidence of an increasing or decreasing trend.
    """

    if not baseline["available"]:
        return {
            "trend_status": "BASELINE",
            "trend_direction": "NO_HISTORICAL_BASELINE",
            "risk_change": 0.0,
            "baseline_delayed_percentage": 0.0,
            "baseline_critical_percentage": 0.0,
            "baseline_risk_exposure": 0.0,
            "trend_confidence": "INSUFFICIENT_HISTORY",
        }

    baseline_delayed_percentage = (
        baseline["average_delayed_percentage"]
    )

    baseline_critical_percentage = (
        baseline["average_critical_percentage"]
    )

    if baseline["batch_count"] < 2:
        return {
            "trend_status": "BASELINE",
            "trend_direction": "INSUFFICIENT_HISTORY",
            "risk_change": 0.0,
            "baseline_delayed_percentage": (
                baseline_delayed_percentage
            ),
            "baseline_critical_percentage": (
                baseline_critical_percentage
            ),
            "baseline_risk_exposure": 0.0,
            "trend_confidence": "LOW",
        }

    current_risk = (
        current["delayed_percentage"] * 0.35
        + current["critical_percentage"] * 0.40
        + current["risk_exposure_score"] * 0.25
    )

    baseline_risk = (
        baseline_delayed_percentage * 0.35
        + baseline_critical_percentage * 0.40
        + (
            100.0
            - baseline["average_quality_score"]
        ) * 0.25
    )

    risk_change = current_risk - baseline_risk

    if risk_change >= 10:
        direction = "STRONGLY_INCREASING"
        status = "ESCALATING"
    elif risk_change >= 3:
        direction = "INCREASING"
        status = "RISING"
    elif risk_change <= -10:
        direction = "STRONGLY_DECREASING"
        status = "IMPROVING"
    elif risk_change <= -3:
        direction = "DECREASING"
        status = "IMPROVING"
    else:
        direction = "STABLE"
        status = "STABLE"

    return {
        "trend_status": status,
        "trend_direction": direction,
        "risk_change": round(risk_change, 2),
        "baseline_delayed_percentage": (
            baseline_delayed_percentage
        ),
        "baseline_critical_percentage": (
            baseline_critical_percentage
        ),
        "baseline_risk_exposure": round(
            baseline_risk,
            2
        ),
        "trend_confidence": "MEDIUM",
    }


def identify_escalation_signals(current, trend):
    signals = []

    if current["overall_risk_level"] == "CRITICAL":
        signals.append(
            "Overall batch risk level is CRITICAL."
        )

    if current["critical_percentage"] >= 50:
        signals.append(
            "Critical-risk predictions represent at least half of the batch."
        )

    if current["high_critical_percentage"] >= 70:
        signals.append(
            "High and critical predictions represent a large majority of the batch."
        )

    if current["delayed_percentage"] >= 70:
        signals.append(
            "A high percentage of predictions are delayed."
        )

    if current["risk_exposure_score"] >= 70:
        signals.append(
            "Batch risk exposure score is at or above the critical threshold."
        )

    if current["confidence"] < 0.50:
        signals.append(
            "Average AI confidence is below the healthy threshold."
        )

    if trend["trend_status"] in {
        "ESCALATING",
        "RISING"
    }:
        signals.append(
            "Historical comparison indicates increasing operational risk."
        )

    if trend["trend_direction"] == "INSUFFICIENT_HISTORY":
        signals.append(
            "Only one historical batch is available; "
            "risk trend requires additional batches."
        )

    return signals


def determine_escalation_level(
    current,
    trend,
    signals
):
    score = 0.0

    if current["overall_risk_level"] == "CRITICAL":
        score += 40
    elif current["overall_risk_level"] == "HIGH":
        score += 30
    elif current["overall_risk_level"] == "MEDIUM":
        score += 20
    else:
        score += 5

    if current["critical_percentage"] >= 50:
        score += 20
    elif current["critical_percentage"] >= 25:
        score += 10

    if current["delayed_percentage"] >= 70:
        score += 15
    elif current["delayed_percentage"] >= 50:
        score += 8

    if current["risk_exposure_score"] >= 70:
        score += 15
    elif current["risk_exposure_score"] >= 50:
        score += 8

    if current["confidence"] < 0.50:
        score += 5

    if trend["trend_status"] == "ESCALATING":
        score += 10
    elif trend["trend_status"] == "RISING":
        score += 5

    score = min(score, 100.0)

    if score >= 75:
        level = "CRITICAL"
        action = "IMMEDIATE_MANAGER_ATTENTION"
    elif score >= 55:
        level = "HIGH"
        action = "OPERATIONAL_REVIEW_REQUIRED"
    elif score >= 35:
        level = "MEDIUM"
        action = "MONITOR_CLOSELY"
    else:
        level = "LOW"
        action = "CONTINUE_NORMAL_MONITORING"

    return {
        "escalation_score": round(
            score,
            2
        ),
        "escalation_level": level,
        "recommended_action": action,
        "signal_count": len(signals),
    }


def build_recommendation(escalation):
    level = escalation["escalation_level"]

    recommendations = {
        "CRITICAL": (
            "Immediate manager attention required. "
            "Prioritize critical shipments and evaluate mitigation actions."
        ),
        "HIGH": (
            "Operational review required. "
            "Prioritize high-risk shipments and monitor mitigation decisions."
        ),
        "MEDIUM": (
            "Monitor the batch closely and review emerging risk signals."
        ),
        "LOW": (
            "Continue normal AI monitoring and operational processing."
        ),
    }

    return recommendations.get(
        level,
        "Continue AI risk monitoring."
    )


def build_report(
    current,
    baseline,
    trend,
    signals,
    escalation
):
    return {
        "monitor_name": MONITOR_NAME,
        "monitor_version": MONITOR_VERSION,
        "status": "COMPLETED",
        "current_batch_risk": current,
        "historical_baseline": baseline,
        "risk_trend": trend,
        "escalation_signals": signals,
        "escalation": escalation,
        "operational_recommendation": build_recommendation(
            escalation
        ),
        "operational_safety": {
            "risk_report_modified": False,
            "history_modified": False,
            "models_modified": False,
            "predictions_modified": False,
            "retraining_triggered": False,
            "optimization_modified": False,
            "database_modified": False,
        },
    }


def print_summary(
    current,
    baseline,
    trend,
    signals,
    escalation
):
    print()
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI BATCH RISK TREND & ESCALATION ENGINE"
    )
    print("=" * 100)

    print()
    print("CURRENT BATCH RISK")
    print("-" * 100)
    print(
        f"Total Predictions        : "
        f"{current['total_predictions']}"
    )
    print(
        f"Risk Exposure Score      : "
        f"{current['risk_exposure_score']:.2f}%"
    )
    print(
        f"Overall Risk Level       : "
        f"{current['overall_risk_level']}"
    )
    print(
        f"Delayed Percentage       : "
        f"{current['delayed_percentage']:.2f}%"
    )
    print(
        f"Critical Percentage      : "
        f"{current['critical_percentage']:.2f}%"
    )
    print(
        f"High/Critical Percentage : "
        f"{current['high_critical_percentage']:.2f}%"
    )

    print()
    print("HISTORICAL BASELINE")
    print("-" * 100)

    if baseline["available"]:
        print(
            f"Batches Available        : "
            f"{baseline['batch_count']}"
        )
        print(
            f"Average Predictions      : "
            f"{baseline['average_predictions']:.2f}"
        )
        print(
            f"Average Quality Score    : "
            f"{baseline['average_quality_score']:.2f}%"
        )
        print(
            f"Average Validation       : "
            f"{baseline['average_validation_score']:.2f}%"
        )
        print(
            f"Average Confidence       : "
            f"{baseline['average_confidence']:.4f}"
        )
        print(
            f"Average Intelligence     : "
            f"{baseline['average_intelligence']:.4f}"
        )
        print(
            f"Average Delayed          : "
            f"{baseline['average_delayed_predictions']:.2f}"
        )
        print(
            f"Average Critical         : "
            f"{baseline['average_critical_predictions']:.2f}"
        )
    else:
        print(
            "No historical baseline available."
        )

    print()
    print("RISK TREND")
    print("-" * 100)
    print(
        f"Trend Status             : "
        f"{trend['trend_status']}"
    )
    print(
        f"Trend Direction          : "
        f"{trend['trend_direction']}"
    )
    print(
        f"Risk Change              : "
        f"{trend['risk_change']:+.2f}"
    )
    print(
        f"Trend Confidence         : "
        f"{trend['trend_confidence']}"
    )

    if baseline["available"]:
        print(
            f"Baseline Delayed %      : "
            f"{trend['baseline_delayed_percentage']:.2f}%"
        )
        print(
            f"Baseline Critical %     : "
            f"{trend['baseline_critical_percentage']:.2f}%"
        )

    print()
    print("ESCALATION SIGNALS")
    print("-" * 100)

    if signals:
        for index, signal in enumerate(
            signals,
            start=1
        ):
            print(
                f"{index:02d}. {signal}"
            )
    else:
        print(
            "No escalation signals detected."
        )

    print()
    print("ESCALATION DECISION")
    print("-" * 100)
    print(
        f"Escalation Score         : "
        f"{escalation['escalation_score']:.2f}%"
    )
    print(
        f"Escalation Level         : "
        f"{escalation['escalation_level']}"
    )
    print(
        f"Recommended Action       : "
        f"{escalation['recommended_action']}"
    )
    print(
        f"Signal Count             : "
        f"{escalation['signal_count']}"
    )
    print(
        f"Recommendation           : "
        f"{build_recommendation(escalation)}"
    )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 100)
    print(
        "✓ Risk aggregation report was not modified."
    )
    print(
        "✓ Historical batch history was not modified."
    )
    print(
        "✓ Prediction outputs were not modified."
    )
    print(
        "✓ Models were not modified."
    )
    print(
        "✓ Retraining was not triggered."
    )
    print(
        "✓ Optimization was not modified."
    )
    print(
        "✓ Database records were not modified."
    )

    print()
    print("=" * 100)
    print(
        "✓ Batch risk trend and escalation analysis "
        "completed successfully."
    )
    print(
        f"✓ Report saved: {OUTPUT_FILE}"
    )
    print("=" * 100)


def main():
    risk_report = load_json_file(
        RISK_REPORT_FILE,
        "AI batch risk aggregation report"
    )

    if risk_report is None:
        return

    history_data = load_json_file(
        HISTORY_FILE,
        "batch quality history"
    )

    if history_data is None:
        return

    print()
    print(
        "Extracting current batch risk metrics..."
    )

    current = extract_current_risk_metrics(
        risk_report
    )

    print(
        "   ✓ Current batch risk metrics extracted."
    )

    print()
    print(
        "Extracting historical batches..."
    )

    history_batches = extract_history_batches(
        history_data
    )

    print(
        f"   ✓ Historical batches available: "
        f"{len(history_batches)}"
    )

    print()
    print(
        "Calculating historical risk baseline..."
    )

    baseline = calculate_historical_baseline(
        history_batches
    )

    print(
        "   ✓ Historical baseline calculated."
    )

    print()
    print(
        "Analyzing batch risk trend..."
    )

    trend = determine_risk_trend(
        current,
        baseline
    )

    print(
        "   ✓ Risk trend analyzed."
    )

    print()
    print(
        "Identifying escalation signals..."
    )

    signals = identify_escalation_signals(
        current,
        trend
    )

    print(
        f"   ✓ Escalation signals identified: "
        f"{len(signals)}"
    )

    print()
    print(
        "Determining escalation decision..."
    )

    escalation = determine_escalation_level(
        current,
        trend,
        signals
    )

    print(
        f"   ✓ Escalation level: "
        f"{escalation['escalation_level']}"
    )

    report = build_report(
        current,
        baseline,
        trend,
        signals,
        escalation
    )

    print()
    print(
        "Saving risk escalation report..."
    )

    try:
        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=2
            )

        print(
            "   ✓ Report saved."
        )
        print(
            f"     {OUTPUT_FILE}"
        )

    except OSError as exc:
        print(
            "   ✗ Failed to save report:"
        )
        print(
            f"     {exc}"
        )
        return

    print_summary(
        current,
        baseline,
        trend,
        signals,
        escalation
    )


if __name__ == "__main__":
    main()