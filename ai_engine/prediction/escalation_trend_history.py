import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path.cwd()

TREND_REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "escalation_trend_intelligence_report.json"
)

HISTORY_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "escalation_trend_history.json"
)


def load_trend_report():
    print("Searching for AI escalation trend intelligence report...")

    if not TREND_REPORT_FILE.exists():
        print("AI escalation trend intelligence report not found.")
        return None

    try:
        with open(TREND_REPORT_FILE, "r", encoding="utf-8") as file:
            report = json.load(file)

        print("AI escalation trend intelligence report loaded.")
        return report

    except Exception as error:
        print(f"Failed to load trend intelligence report: {error}")
        return None


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        if not isinstance(history, list):
            return []

        return history

    except Exception:
        return []


def extract_history_record(report, existing_records):
    trend_intelligence = report.get("trend_intelligence", {})
    overall_trend = report.get("overall_trend", {})
    risk_trend = report.get("risk_trend", {})
    quality_trend = report.get("ai_quality_trend", {})

    record_number = len(existing_records) + 1

    record_id = (
        "TREND-"
        + datetime.now().strftime("%Y%m%d%H%M%S%f")
    )

    record = {
        "record_id": record_id,
        "record_number": record_number,
        "recorded_at": datetime.now().isoformat(),

        "history_overview": {
            "records_analyzed_by_source_report": report.get(
                "history_overview", {}
            ).get("records_analyzed", 0)
        },

        "overall_trend": {
            "direction": overall_trend.get("direction", "UNKNOWN"),
            "severity": overall_trend.get("severity", "UNKNOWN"),
            "confidence": overall_trend.get("confidence", "UNKNOWN")
        },

        "risk_trend": {
            "direction": risk_trend.get("direction", "UNKNOWN"),
            "severity": risk_trend.get("severity", "UNKNOWN")
        },

        "ai_quality_trend": {
            "direction": quality_trend.get("direction", "UNKNOWN"),
            "confidence_direction": quality_trend.get(
                "confidence_direction",
                "UNKNOWN"
            ),
            "intelligence_direction": quality_trend.get(
                "intelligence_direction",
                "UNKNOWN"
            )
        },

        "trend_intelligence": {
            "level": trend_intelligence.get("level", "UNKNOWN"),
            "status": trend_intelligence.get("status", "UNKNOWN"),
            "confidence": trend_intelligence.get(
                "confidence",
                "UNKNOWN"
            )
        },

        "trend_signals": report.get("trend_signals", [])
    }

    return record


def calculate_history_summary(history):
    total_records = len(history)

    if total_records == 0:
        return {
            "total_records": 0,
            "direction_distribution": {},
            "severity_distribution": {},
            "intelligence_distribution": {},
            "baseline_records": 0,
            "trend_records": 0
        }

    direction_distribution = {}
    severity_distribution = {}
    intelligence_distribution = {}

    baseline_records = 0
    trend_records = 0

    for record in history:
        overall_trend = record.get("overall_trend", {})
        intelligence = record.get("trend_intelligence", {})

        direction = overall_trend.get("direction", "UNKNOWN")
        severity = overall_trend.get("severity", "UNKNOWN")
        level = intelligence.get("level", "UNKNOWN")

        direction_distribution[direction] = (
            direction_distribution.get(direction, 0) + 1
        )

        severity_distribution[severity] = (
            severity_distribution.get(severity, 0) + 1
        )

        intelligence_distribution[level] = (
            intelligence_distribution.get(level, 0) + 1
        )

        if level == "BASELINE":
            baseline_records += 1
        else:
            trend_records += 1

    return {
        "total_records": total_records,
        "direction_distribution": direction_distribution,
        "severity_distribution": severity_distribution,
        "intelligence_distribution": intelligence_distribution,
        "baseline_records": baseline_records,
        "trend_records": trend_records
    }


def save_history(history, summary):
    output = {
        "engine": "AI Escalation Trend History Engine",
        "generated_at": datetime.now().isoformat(),

        "history_summary": summary,

        "records": history
    }

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print("Escalation trend history saved.")


def display_summary(record, summary):
    overall_trend = record.get("overall_trend", {})
    risk_trend = record.get("risk_trend", {})
    intelligence = record.get("trend_intelligence", {})

    print()
    print("=" * 90)
    print("SUPPLYPRESCRIPT - AI ESCALATION TREND HISTORY ENGINE")
    print("=" * 90)

    print()
    print("LATEST TREND RECORD")
    print("-" * 90)
    print(f"Record ID: {record.get('record_id')}")
    print(f"Record Number: {record.get('record_number')}")
    print(f"Recorded At: {record.get('recorded_at')}")

    print()
    print("OVERALL TREND")
    print("-" * 90)
    print(f"Direction: {overall_trend.get('direction')}")
    print(f"Severity: {overall_trend.get('severity')}")
    print(f"Confidence: {overall_trend.get('confidence')}")

    print()
    print("RISK TREND")
    print("-" * 90)
    print(f"Direction: {risk_trend.get('direction')}")
    print(f"Severity: {risk_trend.get('severity')}")

    print()
    print("TREND INTELLIGENCE")
    print("-" * 90)
    print(f"Level: {intelligence.get('level')}")
    print(f"Status: {intelligence.get('status')}")
    print(f"Confidence: {intelligence.get('confidence')}")

    print()
    print("HISTORY SUMMARY")
    print("-" * 90)
    print(f"Total Records: {summary.get('total_records')}")
    print(f"Baseline Records: {summary.get('baseline_records')}")
    print(f"Trend Records: {summary.get('trend_records')}")

    print()
    print("DIRECTION DISTRIBUTION")
    print("-" * 90)

    for direction, count in summary.get(
        "direction_distribution", {}
    ).items():
        print(f"{direction}: {count}")

    print()
    print("INTELLIGENCE DISTRIBUTION")
    print("-" * 90)

    for level, count in summary.get(
        "intelligence_distribution", {}
    ).items():
        print(f"{level}: {count}")

    print()
    print("=" * 90)
    print("AI escalation trend history analysis completed successfully.")
    print(f"History saved: {HISTORY_FILE}")
    print("=" * 90)


def main():
    report = load_trend_report()

    if report is None:
        return

    print()
    print("Loading escalation trend history...")

    history = load_history()

    print(f"Existing history records: {len(history)}")

    print()
    print("Creating new trend history record...")

    record = extract_history_record(
        report,
        history
    )

    history.append(record)

    print("Trend history record created.")

    print()
    print("Calculating history summary...")

    summary = calculate_history_summary(history)

    print("History summary calculated.")

    print()
    print("Saving escalation trend history...")

    save_history(
        history,
        summary
    )

    display_summary(
        record,
        summary
    )


if __name__ == "__main__":
    main()