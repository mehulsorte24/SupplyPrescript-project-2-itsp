import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path.cwd()

PERSISTENCE_REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "escalation_trend_persistence_report.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "escalation_trend_state_report.json"
)


def load_persistence_report():
    print("Searching for AI escalation trend persistence report...")

    if not PERSISTENCE_REPORT_FILE.exists():
        print("AI escalation trend persistence report not found.")
        return None

    try:
        with open(
            PERSISTENCE_REPORT_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            report = json.load(file)

        print("AI escalation trend persistence report loaded.")
        return report

    except Exception as error:
        print(
            f"Failed to load persistence report: {error}"
        )
        return None


def classify_state(report):
    persistence = report.get(
        "persistence_analysis",
        {}
    )

    status = persistence.get(
        "status",
        "UNKNOWN"
    )

    confidence = persistence.get(
        "confidence",
        "LOW"
    )

    if status == "PERSISTENT":
        state = "PERSISTENT"

    elif status == "EMERGING":
        state = "EMERGING"

    elif status == "NON_PERSISTENT":
        state = "NON_PERSISTENT"

    elif status == "INSUFFICIENT_HISTORY":
        state = "BASELINE"

    else:
        state = "UNKNOWN"

    return {
        "state": state,
        "confidence": confidence,
        "source_persistence_status": status
    }


def determine_operational_status(state):
    if state == "PERSISTENT":
        return "SUSTAINED_TREND"

    if state == "EMERGING":
        return "WATCH_TREND"

    if state == "NON_PERSISTENT":
        return "NORMAL_VARIATION"

    if state == "BASELINE":
        return "INSUFFICIENT_HISTORY"

    return "UNKNOWN"


def generate_state_signals(
    report,
    classification,
    operational_status
):
    signals = []

    state = classification.get(
        "state",
        "UNKNOWN"
    )

    confidence = classification.get(
        "confidence",
        "LOW"
    )

    records = report.get(
        "history_overview",
        {}
    ).get(
        "records_analyzed",
        0
    )

    if state == "BASELINE":
        signals.append(
            "The available history is insufficient to establish a confirmed temporal trend."
        )

    elif state == "EMERGING":
        signals.append(
            "The latest trend direction has started to repeat across consecutive records."
        )

    elif state == "PERSISTENT":
        signals.append(
            "The latest trend direction has persisted across multiple consecutive records."
        )

    elif state == "NON_PERSISTENT":
        signals.append(
            "The latest trend direction does not currently show persistence."
        )

    else:
        signals.append(
            "The current trend state could not be classified from the available evidence."
        )

    if confidence == "LOW":
        signals.append(
            "Classification confidence is LOW."
        )

    elif confidence == "MEDIUM":
        signals.append(
            "Classification confidence is MEDIUM."
        )

    elif confidence == "HIGH":
        signals.append(
            "Classification confidence is HIGH."
        )

    if records < 2:
        signals.append(
            "Additional trend-history records are required for stronger temporal classification."
        )

    if operational_status == "SUSTAINED_TREND":
        signals.append(
            "The current state indicates a sustained trend condition."
        )

    elif operational_status == "WATCH_TREND":
        signals.append(
            "The current state indicates an emerging trend that should be monitored."
        )

    elif operational_status == "NORMAL_VARIATION":
        signals.append(
            "The current state does not indicate persistent trend behavior."
        )

    elif operational_status == "INSUFFICIENT_HISTORY":
        signals.append(
            "The system remains in a baseline state until additional history is available."
        )

    return signals


def build_report(
    source_report,
    classification,
    operational_status,
    signals
):
    return {
        "engine": "AI Escalation Trend State Classifier",
        "generated_at": datetime.now().isoformat(),

        "source": {
            "persistence_report": str(
                PERSISTENCE_REPORT_FILE
            )
        },

        "history_overview": source_report.get(
            "history_overview",
            {}
        ),

        "classification": classification,

        "operational_status": operational_status,

        "signals": signals,

        "operational_safety": {
            "persistence_report_modified": "NO",
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
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4
        )

    print("Trend state report saved.")


def display_report(report):
    classification = report.get(
        "classification",
        {}
    )

    print()
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI ESCALATION TREND STATE CLASSIFIER"
    )
    print("=" * 90)

    print()
    print("HISTORY OVERVIEW")
    print("-" * 90)

    overview = report.get(
        "history_overview",
        {}
    )

    print(
        f"Records Analyzed: "
        f"{overview.get('records_analyzed', 0)}"
    )

    print(
        f"Valid Direction Records: "
        f"{overview.get('valid_direction_records', 0)}"
    )

    print()
    print("TREND STATE CLASSIFICATION")
    print("-" * 90)

    print(
        f"State: "
        f"{classification.get('state', 'UNKNOWN')}"
    )

    print(
        f"Confidence: "
        f"{classification.get('confidence', 'UNKNOWN')}"
    )

    print(
        f"Source Persistence Status: "
        f"{classification.get('source_persistence_status', 'UNKNOWN')}"
    )

    print()
    print("OPERATIONAL STATUS")
    print("-" * 90)

    print(
        f"Status: "
        f"{report.get('operational_status', 'UNKNOWN')}"
    )

    print()
    print("STATE SIGNALS")
    print("-" * 90)

    signals = report.get(
        "signals",
        []
    )

    for index, signal in enumerate(
        signals,
        start=1
    ):
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
        f"Persistence report modified: "
        f"{safety.get('persistence_report_modified', 'UNKNOWN')}"
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
        "AI escalation trend state classification completed successfully."
    )
    print(
        f"Report saved: {OUTPUT_FILE}"
    )
    print("=" * 90)


def main():
    report = load_persistence_report()

    if report is None:
        return

    print()
    print("Classifying escalation trend state...")

    classification = classify_state(
        report
    )

    print(
        f"Trend state: "
        f"{classification.get('state')}"
    )

    print()
    print("Determining operational status...")

    operational_status = determine_operational_status(
        classification.get("state", "UNKNOWN")
    )

    print(
        f"Operational status: "
        f"{operational_status}"
    )

    print()
    print("Generating state signals...")

    signals = generate_state_signals(
        report,
        classification,
        operational_status
    )

    print(
        f"State signals generated: {len(signals)}"
    )

    print()
    print("Building trend state report...")

    output = build_report(
        report,
        classification,
        operational_status,
        signals
    )

    print("Trend state report built.")

    print()
    print("Saving trend state report...")

    save_report(
        output
    )

    display_report(
        output
    )


if __name__ == "__main__":
    main()