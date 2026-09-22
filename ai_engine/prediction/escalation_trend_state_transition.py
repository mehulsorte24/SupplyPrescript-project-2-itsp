import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path.cwd()
PREDICTION_DIR = PROJECT_ROOT / "ai_engine" / "prediction"

HISTORY_FILE = (
    PREDICTION_DIR / "escalation_trend_state_history.json"
)

OUTPUT_REPORT_FILE = (
    PREDICTION_DIR / "escalation_trend_state_transition_report.json"
)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_state_history():
    print("Searching for AI escalation trend state history...")

    if not HISTORY_FILE.exists():
        raise FileNotFoundError(
            f"State history file not found: {HISTORY_FILE}"
        )

    history = load_json(HISTORY_FILE)

    if not isinstance(history, list):
        raise ValueError(
            "State history must contain a JSON list."
        )

    print("AI escalation trend state history loaded.")

    return history


def get_valid_records(history):
    valid_records = []

    for record in history:
        if not isinstance(record, dict):
            continue

        if "state" not in record:
            continue

        valid_records.append(record)

    return valid_records


def classify_transition(previous_state, current_state):
    if previous_state is None:
        return {
            "transition": "INITIAL_STATE",
            "transition_type": "INITIALIZATION",
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


def analyze_transitions(records):
    transitions = []

    if len(records) < 2:
        return transitions

    for index in range(1, len(records)):
        previous_record = records[index - 1]
        current_record = records[index]

        previous_state = previous_record.get(
            "state",
            "UNKNOWN"
        )

        current_state = current_record.get(
            "state",
            "UNKNOWN"
        )

        classification = classify_transition(
            previous_state,
            current_state
        )

        transition_record = {
            "transition_index": index,
            "previous_record_id": previous_record.get(
                "record_id",
                "UNKNOWN"
            ),
            "current_record_id": current_record.get(
                "record_id",
                "UNKNOWN"
            ),
            "previous_state": previous_state,
            "current_state": current_state,
            "transition": classification["transition"],
            "transition_type": classification[
                "transition_type"
            ],
            "severity": classification["severity"]
        }

        transitions.append(transition_record)

    return transitions


def build_transition_distribution(transitions):
    distribution = {}

    for transition in transitions:
        transition_type = transition.get(
            "transition_type",
            "UNKNOWN"
        )

        distribution[transition_type] = (
            distribution.get(transition_type, 0) + 1
        )

    return distribution


def build_state_distribution(records):
    distribution = {}

    for record in records:
        state = record.get(
            "state",
            "UNKNOWN"
        )

        distribution[state] = (
            distribution.get(state, 0) + 1
        )

    return distribution


def determine_operational_status(
    records,
    transitions
):
    if len(records) < 2:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "confidence": "LOW",
            "reason": (
                "At least two valid state-history records "
                "are required to analyze a state transition."
            )
        }

    if not transitions:
        return {
            "status": "NO_TRANSITION",
            "confidence": "LOW",
            "reason": (
                "No state transitions were available "
                "for analysis."
            )
        }

    latest_transition = transitions[-1]

    transition_type = latest_transition.get(
        "transition_type",
        "UNKNOWN"
    )

    if transition_type == "DETERIORATION":
        return {
            "status": "DETERIORATING",
            "confidence": "MEDIUM",
            "reason": (
                "The latest recorded state transition "
                "indicates deterioration."
            )
        }

    if transition_type == "IMPROVEMENT":
        return {
            "status": "IMPROVING",
            "confidence": "MEDIUM",
            "reason": (
                "The latest recorded state transition "
                "indicates improvement."
            )
        }

    if transition_type == "STABILIZATION":
        return {
            "status": "STABILIZING",
            "confidence": "MEDIUM",
            "reason": (
                "The latest recorded state transition "
                "indicates stabilization."
            )
        }

    if transition_type == "UNCHANGED":
        return {
            "status": "STATE_UNCHANGED",
            "confidence": "MEDIUM",
            "reason": (
                "The latest state remains unchanged "
                "from the previous state."
            )
        }

    return {
        "status": "STATE_CHANGE",
        "confidence": "LOW",
        "reason": (
            "A state transition was detected, but "
            "its operational direction is not classified."
        )
    }


def build_transition_signals(
    records,
    transitions,
    operational_status
):
    signals = []

    if len(records) < 2:
        signals.append(
            "At least two valid state-history records "
            "are required for transition analysis."
        )

        signals.append(
            "The current state remains a baseline "
            "until additional history is available."
        )

        signals.append(
            "Transition confidence is LOW."
        )

        return signals

    if transitions:
        latest_transition = transitions[-1]

        signals.append(
            "A state transition is available for analysis."
        )

        signals.append(
            f"Latest transition: "
            f"{latest_transition['transition']}."
        )

        signals.append(
            f"Transition classification: "
            f"{latest_transition['transition_type']}."
        )

        if latest_transition["severity"] == "HIGH":
            signals.append(
                "The latest transition has HIGH severity "
                "and requires closer operational monitoring."
            )

    else:
        signals.append(
            "No state transitions are available."
        )

    signals.append(
        f"Operational status: "
        f"{operational_status['status']}."
    )

    return signals


def build_report(
    records,
    transitions,
    state_distribution,
    transition_distribution,
    operational_status,
    signals
):
    latest_record = None

    if records:
        latest_record = records[-1]

    latest_transition = None

    if transitions:
        latest_transition = transitions[-1]

    report = {
        "engine": (
            "AI Escalation Trend State Transition Analyzer"
        ),
        "generated_at": datetime.now().isoformat(),
        "history_overview": {
            "records_analyzed": len(records),
            "transition_records": len(transitions),
            "unique_states": len(state_distribution),
            "unique_transition_types": len(
                transition_distribution
            )
        },
        "state_distribution": state_distribution,
        "transition_distribution": transition_distribution,
        "latest_state": latest_record,
        "latest_transition": latest_transition,
        "operational_analysis": operational_status,
        "signals": signals,
        "operational_safety": {
            "state_history_modified": "NO",
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
        "AI ESCALATION TREND STATE TRANSITION ANALYZER"
    )
    print("=" * 90)

    try:
        history = load_state_history()

        print()
        print("Validating state-history records...")

        records = get_valid_records(history)

        print(
            f"Records loaded: {len(history)}"
        )

        print(
            f"Valid records: {len(records)}"
        )

        print()
        print("Analyzing state transitions...")

        transitions = analyze_transitions(records)

        print(
            f"Transitions identified: "
            f"{len(transitions)}"
        )

        print()
        print("Building state distribution...")

        state_distribution = build_state_distribution(
            records
        )

        print(
            f"Unique states: "
            f"{len(state_distribution)}"
        )

        print()
        print("Building transition distribution...")

        transition_distribution = (
            build_transition_distribution(
                transitions
            )
        )

        print(
            f"Transition types: "
            f"{len(transition_distribution)}"
        )

        print()
        print("Determining operational status...")

        operational_status = determine_operational_status(
            records,
            transitions
        )

        print(
            f"Operational status: "
            f"{operational_status['status']}"
        )

        print(
            f"Confidence: "
            f"{operational_status['confidence']}"
        )

        print()
        print("Generating transition signals...")

        signals = build_transition_signals(
            records,
            transitions,
            operational_status
        )

        print(
            f"Signals generated: "
            f"{len(signals)}"
        )

        print()
        print("Building transition analysis report...")

        report = build_report(
            records,
            transitions,
            state_distribution,
            transition_distribution,
            operational_status,
            signals
        )

        print("Transition analysis report built.")

        print()
        print("Saving transition analysis report...")

        save_json(
            OUTPUT_REPORT_FILE,
            report
        )

        print("Transition analysis report saved.")

        print()
        print("=" * 90)
        print("HISTORY OVERVIEW")
        print("-" * 90)
        print(
            f"Records Analyzed: "
            f"{report['history_overview']['records_analyzed']}"
        )
        print(
            f"Transition Records: "
            f"{report['history_overview']['transition_records']}"
        )
        print(
            f"Unique States: "
            f"{report['history_overview']['unique_states']}"
        )
        print(
            f"Unique Transition Types: "
            f"{report['history_overview']['unique_transition_types']}"
        )

        print()
        print("STATE DISTRIBUTION")
        print("-" * 90)

        if state_distribution:
            for state, count in (
                state_distribution.items()
            ):
                print(
                    f"{state}: {count}"
                )
        else:
            print("No valid states available.")

        print()
        print("TRANSITION DISTRIBUTION")
        print("-" * 90)

        if transition_distribution:
            for transition_type, count in (
                transition_distribution.items()
            ):
                print(
                    f"{transition_type}: {count}"
                )
        else:
            print("No transitions available.")

        print()
        print("OPERATIONAL ANALYSIS")
        print("-" * 90)
        print(
            f"Status: "
            f"{operational_status['status']}"
        )
        print(
            f"Confidence: "
            f"{operational_status['confidence']}"
        )
        print(
            f"Reason: "
            f"{operational_status['reason']}"
        )

        print()
        print("TRANSITION SIGNALS")
        print("-" * 90)

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
        print("State history modified: NO")
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
            "AI escalation trend state transition "
            "analysis completed successfully."
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
            f"Failed to analyze state transitions: "
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