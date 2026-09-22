import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path.cwd()
PREDICTION_DIR = PROJECT_ROOT / "ai_engine" / "prediction"

STATE_REPORT_FILE = (
    PREDICTION_DIR / "escalation_trend_state_report.json"
)

STATE_HISTORY_FILE = (
    PREDICTION_DIR / "escalation_trend_state_history.json"
)

OUTPUT_REPORT_FILE = (
    PREDICTION_DIR / "escalation_trend_state_history_report.json"
)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_state_report():
    print("Searching for AI escalation trend state report...")

    if not STATE_REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Escalation trend state report not found: "
            f"{STATE_REPORT_FILE}"
        )

    report = load_json(STATE_REPORT_FILE)

    if not isinstance(report, dict):
        raise ValueError(
            "Escalation trend state report must be a JSON object."
        )

    print("AI escalation trend state report loaded.")

    return report


def load_state_history():
    if not STATE_HISTORY_FILE.exists():
        return []

    try:
        history = load_json(STATE_HISTORY_FILE)

        if not isinstance(history, list):
            return []

        return history

    except (json.JSONDecodeError, OSError):
        return []


def extract_state_snapshot(report):
    classification = report.get(
        "classification",
        {}
    )

    if not isinstance(classification, dict):
        classification = {}

    state = classification.get(
        "state",
        "UNKNOWN"
    )

    confidence = classification.get(
        "confidence",
        "LOW"
    )

    source_persistence_status = classification.get(
        "source_persistence_status",
        "UNKNOWN"
    )

    operational_status = report.get(
        "operational_status",
        "UNKNOWN"
    )

    signals = report.get(
        "signals",
        []
    )

    if not isinstance(signals, list):
        signals = []

    snapshot = {
        "record_id": datetime.now().strftime(
            "STATE-%Y%m%d%H%M%S%f"
        ),
        "recorded_at": datetime.now().isoformat(),
        "state": state,
        "confidence": confidence,
        "source_persistence_status": (
            source_persistence_status
        ),
        "operational_status": operational_status,
        "signal_count": len(signals)
    }

    return snapshot


def classify_transition(
    previous_state,
    current_state
):
    if previous_state is None:
        return {
            "transition": "INITIAL_STATE",
            "transition_type": "BASELINE",
            "severity": "LOW"
        }

    if previous_state == current_state:
        return {
            "transition": (
                f"{previous_state}_TO_{current_state}"
            ),
            "transition_type": "UNCHANGED",
            "severity": "LOW"
        }

    improving_states = {
        "IMPROVING",
        "RECOVERING"
    }

    worsening_states = {
        "WORSENING",
        "DETERIORATING"
    }

    if current_state in improving_states:
        return {
            "transition": (
                f"{previous_state}_TO_{current_state}"
            ),
            "transition_type": "IMPROVEMENT",
            "severity": "MEDIUM"
        }

    if current_state in worsening_states:
        return {
            "transition": (
                f"{previous_state}_TO_{current_state}"
            ),
            "transition_type": "DETERIORATION",
            "severity": "HIGH"
        }

    if current_state == "STABLE":
        return {
            "transition": (
                f"{previous_state}_TO_{current_state}"
            ),
            "transition_type": "STABILIZATION",
            "severity": "LOW"
        }

    if current_state == "BASELINE":
        return {
            "transition": (
                f"{previous_state}_TO_{current_state}"
            ),
            "transition_type": "BASELINE_RESET",
            "severity": "LOW"
        }

    return {
        "transition": (
            f"{previous_state}_TO_{current_state}"
        ),
        "transition_type": "STATE_CHANGE",
        "severity": "MEDIUM"
    }


def build_state_history_report(
    history,
    current_snapshot,
    transition
):
    total_records = len(history)

    state_distribution = {}

    for record in history:
        if not isinstance(record, dict):
            continue

        state = record.get(
            "state",
            "UNKNOWN"
        )

        state_distribution[state] = (
            state_distribution.get(state, 0) + 1
        )

    previous_state = None

    if len(history) >= 2:
        previous_record = history[-2]

        if isinstance(previous_record, dict):
            previous_state = previous_record.get(
                "state"
            )

    current_state = current_snapshot.get(
        "state",
        "UNKNOWN"
    )

    signals = []

    if total_records == 1:
        signals.append(
            "Only one state-history record is available; "
            "temporal state changes cannot yet be confirmed."
        )

    if previous_state is None:
        signals.append(
            "The current state is being established as "
            "the initial operational baseline."
        )

    elif previous_state == current_state:
        signals.append(
            "The current trend state is unchanged from "
            "the previous recorded state."
        )

    else:
        signals.append(
            f"The trend state changed from "
            f"{previous_state} to {current_state}."
        )

    if current_snapshot.get("confidence") == "LOW":
        signals.append(
            "Current trend-state confidence is LOW."
        )

    if current_snapshot.get(
        "source_persistence_status"
    ) == "INSUFFICIENT_HISTORY":
        signals.append(
            "The source persistence analysis still "
            "requires additional historical records."
        )

    report = {
        "engine": (
            "AI Escalation Trend State History Engine"
        ),
        "generated_at": datetime.now().isoformat(),
        "history_overview": {
            "records_analyzed": total_records,
            "previous_state": previous_state,
            "current_state": current_state,
            "unique_states": len(state_distribution)
        },
        "state_distribution": state_distribution,
        "current_state": current_snapshot,
        "transition_analysis": {
            "transition": transition["transition"],
            "transition_type": transition[
                "transition_type"
            ],
            "severity": transition["severity"]
        },
        "history_signals": signals,
        "operational_safety": {
            "state_report_modified": "NO",
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

    return report


def main():
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - "
        "AI ESCALATION TREND STATE HISTORY ENGINE"
    )
    print("=" * 90)

    try:
        state_report = load_state_report()

        print()
        print("Loading existing state history...")

        history = load_state_history()

        print(
            f"Existing state-history records: "
            f"{len(history)}"
        )

        print()
        print("Creating current state snapshot...")

        current_snapshot = extract_state_snapshot(
            state_report
        )

        previous_state = None

        if history:
            last_record = history[-1]

            if isinstance(last_record, dict):
                previous_state = last_record.get(
                    "state"
                )

        current_state = current_snapshot.get(
            "state",
            "UNKNOWN"
        )

        print(
            f"Previous state: "
            f"{previous_state or 'NONE'}"
        )

        print(
            f"Current state: "
            f"{current_state}"
        )

        print()
        print("Analyzing state transition...")

        transition = classify_transition(
            previous_state,
            current_state
        )

        print(
            f"Transition: "
            f"{transition['transition']}"
        )

        print(
            f"Transition type: "
            f"{transition['transition_type']}"
        )

        print(
            f"Severity: "
            f"{transition['severity']}"
        )

        history.append(current_snapshot)

        print()
        print("Saving state history...")

        save_json(
            STATE_HISTORY_FILE,
            history
        )

        print("State history saved.")

        print()
        print("Building state-history report...")

        report = build_state_history_report(
            history,
            current_snapshot,
            transition
        )

        print("State-history report built.")

        print()
        print("Saving state-history report...")

        save_json(
            OUTPUT_REPORT_FILE,
            report
        )

        print("State-history report saved.")

        print()
        print("=" * 90)
        print("STATE HISTORY OVERVIEW")
        print("-" * 90)

        print(
            f"Records Analyzed: "
            f"{report['history_overview']['records_analyzed']}"
        )

        print(
            f"Previous State: "
            f"{report['history_overview']['previous_state'] or 'NONE'}"
        )

        print(
            f"Current State: "
            f"{report['history_overview']['current_state']}"
        )

        print(
            f"Unique States: "
            f"{report['history_overview']['unique_states']}"
        )

        print()
        print("STATE DISTRIBUTION")
        print("-" * 90)

        for state, count in (
            report["state_distribution"].items()
        ):
            print(
                f"{state}: {count}"
            )

        print()
        print("STATE TRANSITION")
        print("-" * 90)

        print(
            f"Transition: "
            f"{report['transition_analysis']['transition']}"
        )

        print(
            f"Type: "
            f"{report['transition_analysis']['transition_type']}"
        )

        print(
            f"Severity: "
            f"{report['transition_analysis']['severity']}"
        )

        print()
        print("HISTORY SIGNALS")
        print("-" * 90)

        for index, signal in enumerate(
            report["history_signals"],
            start=1
        ):
            print(
                f"{index:02d}. {signal}"
            )

        print()
        print("OPERATIONAL SAFETY")
        print("-" * 90)
        print("State report modified: NO")
        print("Trend history modified: NO")
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
            "AI escalation trend state history "
            "completed successfully."
        )
        print(
            f"History saved: "
            f"{STATE_HISTORY_FILE}"
        )
        print(
            f"Report saved: "
            f"{OUTPUT_REPORT_FILE}"
        )
        print("=" * 90)

    except FileNotFoundError as error:
        print()
        print("ERROR")
        print("-" * 90)
        print(error)

    except ValueError as error:
        print()
        print("ERROR")
        print("-" * 90)
        print(error)

    except (
        json.JSONDecodeError,
        OSError
    ) as error:
        print()
        print("ERROR")
        print("-" * 90)
        print(
            f"Failed to process state history: "
            f"{error}"
        )

    except Exception as error:
        print()
        print("UNEXPECTED ERROR")
        print("-" * 90)
        print(
            f"{type(error).__name__}: {error}"
        )


if __name__ == "__main__":
    main()