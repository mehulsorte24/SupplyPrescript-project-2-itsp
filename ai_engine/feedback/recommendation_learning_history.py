import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path.cwd()

SIGNAL_FILE = (
    BASE_DIR
    / "ai_engine"
    / "feedback"
    / "recommendation_learning_signal.json"
)

HISTORY_FILE = (
    BASE_DIR
    / "ai_engine"
    / "feedback"
    / "recommendation_learning_history.json"
)


def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found:\n{file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_learning_signal():
    print("Loading recommendation learning signal...")

    signal = load_json(SIGNAL_FILE)

    print("   ✓ Recommendation learning signal loaded.")

    return signal


def load_history():
    if not HISTORY_FILE.exists():
        return {
            "system": "SupplyPrescript",
            "module": "AI Recommendation Learning History Engine",
            "engine_version": "1.0",
            "status": "INITIALIZED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "history": []
        }

    try:
        history = load_json(HISTORY_FILE)

        if not isinstance(history, dict):
            raise ValueError("Learning history must be a JSON object.")

        if "history" not in history:
            history["history"] = []

        if not isinstance(history["history"], list):
            raise ValueError("Learning history must be a list.")

        return history

    except json.JSONDecodeError:
        print("   ⚠ Existing history file is invalid.")
        print("   ✓ Starting a new learning history.")

        return {
            "system": "SupplyPrescript",
            "module": "AI Recommendation Learning History Engine",
            "engine_version": "1.0",
            "status": "INITIALIZED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "history": []
        }


def create_history_record(signal):
    decision = signal.get("decision", {})
    recommendation = signal.get("ai_recommendation", {})
    outcome_reference = signal.get("outcome_reference", {})
    prediction_outcome = signal.get("prediction_outcome", {})
    learning_signal = signal.get("learning_signal", {})
    recommendation_learning = signal.get(
        "recommendation_learning",
        {}
    )

    return {
        "history_record_id": (
            f"LEARN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        ),
        "recorded_at": datetime.now(timezone.utc).isoformat(),

        "decision": {
            "decision_id": decision.get("decision_id"),
            "selected_action": decision.get("selected_action"),
            "decision_source": decision.get("decision_source"),
        },

        "recommendation": {
            "recommended_action": recommendation.get(
                "recommended_action"
            ),
            "recommendation_rank": recommendation.get(
                "recommendation_rank"
            ),
            "recommendation_score": recommendation.get(
                "recommendation_score"
            ),
        },

        "outcome_reference": {
            "shipment_id": outcome_reference.get("shipment_id"),
            "shipment_specific_decision_link": (
                outcome_reference.get(
                    "shipment_specific_decision_link",
                    False
                )
            ),
        },

        "prediction_outcome": {
            "predicted_status": prediction_outcome.get(
                "predicted_status"
            ),
            "actual_status": prediction_outcome.get(
                "actual_status"
            ),
            "classification_correct": prediction_outcome.get(
                "classification_correct"
            ),
            "predicted_delay_days": prediction_outcome.get(
                "predicted_delay_days"
            ),
            "actual_delay_days": prediction_outcome.get(
                "actual_delay_days"
            ),
            "absolute_delay_error_days": prediction_outcome.get(
                "absolute_delay_error_days"
            ),
        },

        "learning_signal": {
            "signal_type": learning_signal.get(
                "signal_type"
            ),
            "learning_status": learning_signal.get(
                "learning_status"
            ),
            "learning_strength": learning_signal.get(
                "learning_strength"
            ),
            "learning_ready": learning_signal.get(
                "learning_ready"
            ),
        },

        "recommendation_learning": {
            "manager_action_recorded": (
                recommendation_learning.get(
                    "manager_action_recorded",
                    False
                )
            ),
            "actual_outcome_recorded": (
                recommendation_learning.get(
                    "actual_outcome_recorded",
                    False
                )
            ),
            "recommendation_evaluation_available": (
                recommendation_learning.get(
                    "recommendation_evaluation_available",
                    False
                )
            ),
            "causal_effect_established": (
                recommendation_learning.get(
                    "causal_effect_established",
                    False
                )
            ),
            "shipment_specific_link_available": (
                recommendation_learning.get(
                    "shipment_specific_link_available",
                    False
                )
            ),
            "recommendation_update_status": (
                recommendation_learning.get(
                    "recommendation_update_status"
                )
            ),
        },
    }


def calculate_statistics(history_records):
    total_records = len(history_records)

    positive_signals = 0
    negative_signals = 0
    partial_signals = 0
    delay_error_signals = 0
    insufficient_signals = 0
    update_ready = 0
    update_blocked = 0

    for record in history_records:
        signal_type = record.get(
            "learning_signal",
            {}
        ).get(
            "signal_type"
        )

        update_status = record.get(
            "recommendation_learning",
            {}
        ).get(
            "recommendation_update_status"
        )

        if signal_type == "POSITIVE_OUTCOME_SIGNAL":
            positive_signals += 1

        elif signal_type == "NEGATIVE_OUTCOME_SIGNAL":
            negative_signals += 1

        elif signal_type == "PARTIAL_POSITIVE_OUTCOME_SIGNAL":
            partial_signals += 1

        elif signal_type == "DELAY_ERROR_OUTCOME_SIGNAL":
            delay_error_signals += 1

        else:
            insufficient_signals += 1

        if update_status == (
            "READY_FOR_RECOMMENDATION_WEIGHT_UPDATE"
        ):
            update_ready += 1

        elif update_status == (
            "LEARNING_SIGNAL_AVAILABLE_BUT_UPDATE_BLOCKED"
        ):
            update_blocked += 1

    return {
        "total_learning_records": total_records,
        "positive_outcome_signals": positive_signals,
        "negative_outcome_signals": negative_signals,
        "partial_positive_signals": partial_signals,
        "delay_error_signals": delay_error_signals,
        "insufficient_signals": insufficient_signals,
        "recommendation_updates_ready": update_ready,
        "recommendation_updates_blocked": update_blocked,
    }


def append_learning_record(history, record):
    history["history"].append(record)

    history["history"] = history["history"][
        -1000:
    ]

    return history


def build_history(signal, history):
    record = create_history_record(signal)

    append_learning_record(history, record)

    statistics = calculate_statistics(
        history["history"]
    )

    history["system"] = "SupplyPrescript"
    history["module"] = (
        "AI Recommendation Learning History Engine"
    )
    history["engine_version"] = "1.0"
    history["status"] = "COMPLETED"
    history["updated_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    history["statistics"] = statistics

    history["learning_policy"] = {
        "automatic_recommendation_weight_updates": False,
        "automatic_model_updates": False,
        "causal_effect_required_for_weight_update": True,
        "shipment_specific_link_required": True,
        "minimum_history_policy": (
            "Accumulate historical learning signals before "
            "recommendation weight adjustment."
        ),
    }

    history["operational_safety"] = {
        "recommendation_weights_modified": False,
        "model_weights_modified": False,
        "models_retrained": False,
        "predictions_modified": False,
        "recommendation_reports_modified": False,
        "manager_decisions_modified": False,
        "shipments_modified": False,
        "database_modified": False,
        "business_decision_executed": False,
    }

    return history


def print_report(history):
    statistics = history["statistics"]
    latest_record = history["history"][-1]

    print()
    print("=" * 90)
    print("RECOMMENDATION LEARNING HISTORY")
    print("-" * 90)

    print(
        f"History Records: "
        f"{statistics['total_learning_records']}"
    )

    print(
        f"Positive Signals: "
        f"{statistics['positive_outcome_signals']}"
    )

    print(
        f"Negative Signals: "
        f"{statistics['negative_outcome_signals']}"
    )

    print(
        f"Partial Positive Signals: "
        f"{statistics['partial_positive_signals']}"
    )

    print(
        f"Delay Error Signals: "
        f"{statistics['delay_error_signals']}"
    )

    print(
        f"Insufficient Signals: "
        f"{statistics['insufficient_signals']}"
    )

    print()
    print("LATEST LEARNING RECORD")
    print("-" * 90)

    print(
        f"History Record ID: "
        f"{latest_record['history_record_id']}"
    )

    print(
        f"Decision ID: "
        f"{latest_record['decision']['decision_id']}"
    )

    print(
        f"Selected Action: "
        f"{latest_record['decision']['selected_action']}"
    )

    print(
        f"Recommended Action: "
        f"{latest_record['recommendation']['recommended_action']}"
    )

    print(
        f"Shipment Reference: "
        f"{latest_record['outcome_reference']['shipment_id']}"
    )

    print(
        f"Learning Signal: "
        f"{latest_record['learning_signal']['signal_type']}"
    )

    print(
        f"Learning Strength: "
        f"{latest_record['learning_signal']['learning_strength']}"
    )

    print(
        f"Recommendation Update Status: "
        f"{latest_record['recommendation_learning']['recommendation_update_status']}"
    )

    print()
    print("LEARNING POLICY")
    print("-" * 90)

    print("Automatic Recommendation Weight Updates: NO")
    print("Automatic Model Updates: NO")
    print("Causal Effect Required: YES")
    print("Shipment-Specific Link Required: YES")

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)

    print("Recommendation Weights Modified: NO")
    print("Model Weights Modified: NO")
    print("Models Retrained: NO")
    print("Predictions Modified: NO")
    print("Business Decision Executed: NO")


def main():
    print("=" * 90)
    print("SUPPLYPRESCRIPT - AI RECOMMENDATION LEARNING HISTORY ENGINE")
    print("=" * 90)

    try:
        signal = load_learning_signal()

        print()
        print("Loading recommendation learning history...")

        history = load_history()

        print(
            f"   ✓ Existing history records: "
            f"{len(history.get('history', []))}"
        )

        print()
        print("Appending latest learning signal...")

        history = build_history(
            signal,
            history
        )

        print("   ✓ Learning signal added to history.")

        print_report(history)

        print()
        print("Saving recommendation learning history...")

        save_json(
            HISTORY_FILE,
            history
        )

        print("   ✓ Learning history saved.")

        print()
        print("=" * 90)
        print(
            "AI RECOMMENDATION LEARNING HISTORY ENGINE COMPLETED"
        )
        print("=" * 90)
        print(f"History saved: {HISTORY_FILE}")
        print("=" * 90)

    except Exception as error:
        print()
        print(
            "✗ Recommendation learning history engine failed."
        )
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()