import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path.cwd()

HISTORY_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "escalation_trend_history.json"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "escalation_trend_persistence_report.json"
)


def load_history():
    print("Searching for AI escalation trend history...")

    if not HISTORY_FILE.exists():
        print("AI escalation trend history not found.")
        return None

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        records = data.get("records", [])

        if not isinstance(records, list):
            print("Invalid escalation trend history format.")
            return None

        print("AI escalation trend history loaded.")
        return records

    except Exception as error:
        print(f"Failed to load escalation trend history: {error}")
        return None


def extract_direction_records(records):
    directions = []

    for record in records:
        overall_trend = record.get("overall_trend", {})
        direction = overall_trend.get("direction", "UNKNOWN")

        directions.append(direction)

    return directions


def calculate_direction_distribution(directions):
    distribution = {}

    for direction in directions:
        distribution[direction] = (
            distribution.get(direction, 0) + 1
        )

    return distribution


def calculate_consecutive_run(directions):
    if not directions:
        return {
            "direction": "UNKNOWN",
            "length": 0
        }

    latest_direction = directions[-1]

    if latest_direction == "UNKNOWN":
        return {
            "direction": "UNKNOWN",
            "length": 1
        }

    run_length = 0

    for direction in reversed(directions):
        if direction == latest_direction:
            run_length += 1
        else:
            break

    return {
        "direction": latest_direction,
        "length": run_length
    }


def determine_persistence_status(records, directions):
    record_count = len(records)

    if record_count < 2:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "confidence": "LOW",
            "reason": (
                "At least two trend records are required "
                "to evaluate persistence."
            )
        }

    valid_directions = [
        direction
        for direction in directions
        if direction != "UNKNOWN"
    ]

    if len(valid_directions) < 2:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "confidence": "LOW",
            "reason": (
                "At least two valid temporal trend directions "
                "are required."
            )
        }

    latest_direction = valid_directions[-1]

    consecutive_count = 0

    for direction in reversed(valid_directions):
        if direction == latest_direction:
            consecutive_count += 1
        else:
            break

    if consecutive_count >= 3:
        return {
            "status": "PERSISTENT",
            "confidence": "HIGH",
            "reason": (
                "The latest trend direction has persisted "
                "for at least three consecutive records."
            )
        }

    if consecutive_count == 2:
        return {
            "status": "EMERGING",
            "confidence": "MEDIUM",
            "reason": (
                "The latest trend direction appears in "
                "two consecutive records."
            )
        }

    return {
        "status": "NON_PERSISTENT",
        "confidence": "MEDIUM",
        "reason": (
            "The latest trend direction does not show "
            "consecutive persistence."
        )
    }


def determine_latest_state(records):
    if not records:
        return {
            "direction": "UNKNOWN",
            "severity": "UNKNOWN",
            "intelligence_level": "UNKNOWN",
            "status": "UNKNOWN"
        }

    latest = records[-1]

    overall_trend = latest.get("overall_trend", {})
    intelligence = latest.get("trend_intelligence", {})

    return {
        "direction": overall_trend.get(
            "direction",
            "UNKNOWN"
        ),
        "severity": overall_trend.get(
            "severity",
            "UNKNOWN"
        ),
        "intelligence_level": intelligence.get(
            "level",
            "UNKNOWN"
        ),
        "status": intelligence.get(
            "status",
            "UNKNOWN"
        )
    }


def generate_signals(
    records,
    directions,
    distribution,
    consecutive_run,
    persistence
):
    signals = []

    if len(records) < 2:
        signals.append(
            "At least two trend records are required for temporal persistence analysis."
        )

    if "UNKNOWN" in directions:
        signals.append(
            "One or more trend records contain an UNKNOWN direction."
        )

    if consecutive_run["length"] >= 3:
        signals.append(
            "The latest trend direction has persisted across at least three records."
        )

    elif consecutive_run["length"] == 2:
        signals.append(
            "The latest trend direction has appeared in two consecutive records."
        )

    if persistence["status"] == "NON_PERSISTENT":
        signals.append(
            "The latest valid trend direction is not currently persistent."
        )

    if len(distribution) > 1:
        signals.append(
            "Multiple trend directions are present in the available history."
        )

    if len(records) >= 2:
        signals.append(
            "Temporal comparison is available for the stored trend records."
        )

    if not signals:
        signals.append(
            "No additional persistence signals were identified."
        )

    return signals


def build_report(
    records,
    directions,
    distribution,
    consecutive_run,
    persistence,
    latest_state,
    signals
):
    return {
        "engine": "AI Escalation Trend Persistence Analyzer",
        "generated_at": datetime.now().isoformat(),

        "history_overview": {
            "records_analyzed": len(records),
            "valid_direction_records": len(
                [
                    direction
                    for direction in directions
                    if direction != "UNKNOWN"
                ]
            )
        },

        "direction_distribution": distribution,

        "latest_state": latest_state,

        "consecutive_trend_run": consecutive_run,

        "persistence_analysis": persistence,

        "signals": signals,

        "operational_safety": {
            "trend_history_modified": "NO",
            "escalation_history_modified": "NO",
            "prediction_outputs_modified": "NO",
            "risk_reports_modified": "NO",
            "models_modified": "NO",
            "retraining_triggered": "NO",
            "optimization_modified": "NO",
            "database_modified": "NO"
        }
    }


def save_report(report):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4
        )

    print("Persistence analysis report saved.")


def display_report(report):
    overview = report.get("history_overview", {})
    latest = report.get("latest_state", {})
    run = report.get("consecutive_trend_run", {})
    persistence = report.get("persistence_analysis", {})
    signals = report.get("signals", [])

    print()
    print("=" * 90)
    print("SUPPLYPRESCRIPT - AI ESCALATION TREND PERSISTENCE ANALYZER")
    print("=" * 90)

    print()
    print("HISTORY OVERVIEW")
    print("-" * 90)
    print(
        f"Records Analyzed: "
        f"{overview.get('records_analyzed', 0)}"
    )
    print(
        f"Valid Direction Records: "
        f"{overview.get('valid_direction_records', 0)}"
    )

    print()
    print("LATEST TREND STATE")
    print("-" * 90)
    print(
        f"Direction: "
        f"{latest.get('direction', 'UNKNOWN')}"
    )
    print(
        f"Severity: "
        f"{latest.get('severity', 'UNKNOWN')}"
    )
    print(
        f"Intelligence Level: "
        f"{latest.get('intelligence_level', 'UNKNOWN')}"
    )
    print(
        f"Status: "
        f"{latest.get('status', 'UNKNOWN')}"
    )

    print()
    print("CONSECUTIVE TREND RUN")
    print("-" * 90)
    print(
        f"Direction: "
        f"{run.get('direction', 'UNKNOWN')}"
    )
    print(
        f"Length: "
        f"{run.get('length', 0)}"
    )

    print()
    print("PERSISTENCE ANALYSIS")
    print("-" * 90)
    print(
        f"Status: "
        f"{persistence.get('status', 'UNKNOWN')}"
    )
    print(
        f"Confidence: "
        f"{persistence.get('confidence', 'UNKNOWN')}"
    )
    print(
        f"Reason: "
        f"{persistence.get('reason', 'UNKNOWN')}"
    )

    print()
    print("TREND SIGNALS")
    print("-" * 90)

    for index, signal in enumerate(signals, start=1):
        print(
            f"{index:02d}. {signal}"
        )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)

    safety = report.get(
        "operational_safety",
        {}
    )

    print(
        f"Trend history modified: "
        f"{safety.get('trend_history_modified', 'UNKNOWN')}"
    )
    print(
        f"Escalation history modified: "
        f"{safety.get('escalation_history_modified', 'UNKNOWN')}"
    )
    print(
        f"Prediction outputs modified: "
        f"{safety.get('prediction_outputs_modified', 'UNKNOWN')}"
    )
    print(
        f"Risk reports modified: "
        f"{safety.get('risk_reports_modified', 'UNKNOWN')}"
    )
    print(
        f"Models modified: "
        f"{safety.get('models_modified', 'UNKNOWN')}"
    )
    print(
        f"Retraining triggered: "
        f"{safety.get('retraining_triggered', 'UNKNOWN')}"
    )
    print(
        f"Optimization modified: "
        f"{safety.get('optimization_modified', 'UNKNOWN')}"
    )
    print(
        f"Database modified: "
        f"{safety.get('database_modified', 'UNKNOWN')}"
    )

    print()
    print("=" * 90)
    print(
        "AI escalation trend persistence analysis completed successfully."
    )
    print(
        f"Report saved: {REPORT_FILE}"
    )
    print("=" * 90)


def main():
    records = load_history()

    if records is None:
        return

    print()
    print("Extracting trend directions...")

    directions = extract_direction_records(
        records
    )

    print(
        f"Directions extracted: {len(directions)}"
    )

    print()
    print("Calculating direction distribution...")

    distribution = calculate_direction_distribution(
        directions
    )

    print("Direction distribution calculated.")

    print()
    print("Calculating consecutive trend run...")

    consecutive_run = calculate_consecutive_run(
        directions
    )

    print("Consecutive trend run calculated.")

    print()
    print("Determining persistence status...")

    persistence = determine_persistence_status(
        records,
        directions
    )

    print(
        f"Persistence status: "
        f"{persistence.get('status')}"
    )

    print()
    print("Determining latest trend state...")

    latest_state = determine_latest_state(
        records
    )

    print("Latest trend state determined.")

    print()
    print("Generating persistence signals...")

    signals = generate_signals(
        records,
        directions,
        distribution,
        consecutive_run,
        persistence
    )

    print(
        f"Persistence signals generated: {len(signals)}"
    )

    print()
    print("Building persistence report...")

    report = build_report(
        records,
        directions,
        distribution,
        consecutive_run,
        persistence,
        latest_state,
        signals
    )

    print("Persistence report built.")

    print()
    print("Saving persistence report...")

    save_report(
        report
    )

    display_report(
        report
    )


if __name__ == "__main__":
    main()