import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path.cwd()

INPUT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "feedback"
    / "recommendation_outcome_analysis.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "feedback"
    / "recommendation_learning_signal.json"
)


def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found:\n{file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def find_value(data, possible_keys, default=None):
    """
    Recursively searches a nested dictionary for the first matching key.
    This keeps the engine compatible with the existing recommendation
    outcome analysis structure.
    """

    if isinstance(data, dict):
        for key in possible_keys:
            if key in data:
                return data[key]

        for value in data.values():
            result = find_value(value, possible_keys, default)
            if result is not default:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_value(item, possible_keys, default)
            if result is not default:
                return result

    return default


def load_analysis():
    print("Loading recommendation outcome analysis...")

    data = load_json(INPUT_FILE)

    print("   ✓ Recommendation outcome analysis loaded.")

    return data


def extract_context(data):
    decision_id = find_value(
        data,
        ["decision_id"],
        "UNKNOWN"
    )

    selected_action = find_value(
        data,
        ["selected_action"],
        "UNKNOWN"
    )

    decision_source = find_value(
        data,
        ["decision_source"],
        "UNKNOWN"
    )

    recommended_action = find_value(
        data,
        ["recommended_action", "action"],
        "UNKNOWN"
    )

    recommendation_rank = find_value(
        data,
        ["recommendation_rank", "rank"],
        None
    )

    recommendation_score = find_value(
        data,
        ["recommendation_score", "score"],
        None
    )

    shipment_id = find_value(
        data,
        ["shipment_id"],
        None
    )

    predicted_status = find_value(
        data,
        ["predicted_status"],
        None
    )

    actual_status = find_value(
        data,
        ["actual_status"],
        None
    )

    classification_correct = find_value(
        data,
        ["classification_correct"],
        None
    )

    predicted_delay_days = find_value(
        data,
        ["predicted_delay_days", "predicted_delay"],
        None
    )

    actual_delay_days = find_value(
        data,
        ["actual_delay_days", "actual_delay"],
        None
    )

    absolute_delay_error_days = find_value(
        data,
        [
            "absolute_delay_error_days",
            "absolute_delay_error"
        ],
        None
    )

    outcome_evaluation_available = find_value(
        data,
        ["outcome_evaluation_available"],
        False
    )

    observed_outcome_signal = find_value(
        data,
        ["observed_outcome_signal"],
        "INSUFFICIENT_EVIDENCE"
    )

    causal_effect_established = find_value(
        data,
        ["causal_effect_established"],
        False
    )

    recommendation_weight_update_ready = find_value(
        data,
        ["recommendation_weight_update_ready"],
        False
    )

    manager_action_recorded = find_value(
        data,
        ["manager_action_recorded"],
        False
    )

    actual_outcome_recorded = find_value(
        data,
        ["actual_outcome_recorded"],
        False
    )

    recommendation_evaluation_available = find_value(
        data,
        ["recommendation_evaluation_available"],
        False
    )

    shipment_specific_decision_link = find_value(
        data,
        ["shipment_specific_decision_link"],
        False
    )

    return {
        "decision_id": decision_id,
        "selected_action": selected_action,
        "decision_source": decision_source,
        "recommended_action": recommended_action,
        "recommendation_rank": recommendation_rank,
        "recommendation_score": recommendation_score,
        "shipment_id": shipment_id,
        "predicted_status": predicted_status,
        "actual_status": actual_status,
        "classification_correct": classification_correct,
        "predicted_delay_days": predicted_delay_days,
        "actual_delay_days": actual_delay_days,
        "absolute_delay_error_days": absolute_delay_error_days,
        "outcome_evaluation_available": outcome_evaluation_available,
        "observed_outcome_signal": observed_outcome_signal,
        "causal_effect_established": causal_effect_established,
        "recommendation_weight_update_ready": (
            recommendation_weight_update_ready
        ),
        "manager_action_recorded": manager_action_recorded,
        "actual_outcome_recorded": actual_outcome_recorded,
        "recommendation_evaluation_available": (
            recommendation_evaluation_available
        ),
        "shipment_specific_decision_link": (
            shipment_specific_decision_link
        ),
    }


def determine_learning_signal(context):
    outcome_available = context["outcome_evaluation_available"]
    recommendation_evaluated = (
        context["recommendation_evaluation_available"]
    )
    observed_signal = context["observed_outcome_signal"]
    causal_effect = context["causal_effect_established"]
    shipment_link = context["shipment_specific_decision_link"]

    if not outcome_available:
        signal_type = "NO_OUTCOME_EVIDENCE"
        learning_status = "WAITING_FOR_OUTCOME"
        learning_strength = "NONE"
        learning_ready = False

    elif not recommendation_evaluated:
        signal_type = (
            "OUTCOME_AVAILABLE_RECOMMENDATION_NOT_EVALUATED"
        )
        learning_status = (
            "WAITING_FOR_RECOMMENDATION_EVALUATION"
        )
        learning_strength = "LIMITED"
        learning_ready = False

    elif observed_signal == "NEGATIVE_PREDICTION_SIGNAL":
        signal_type = "NEGATIVE_OUTCOME_SIGNAL"
        learning_status = "LEARNING_SIGNAL_AVAILABLE"
        learning_strength = "MODERATE"
        learning_ready = True

    elif observed_signal == "POSITIVE_PREDICTION_SIGNAL":
        signal_type = "POSITIVE_OUTCOME_SIGNAL"
        learning_status = "LEARNING_SIGNAL_AVAILABLE"
        learning_strength = "MODERATE"
        learning_ready = True

    elif observed_signal == "PREDICTION_CORRECT_WITH_DELAY_ERROR":
        signal_type = "PARTIAL_POSITIVE_OUTCOME_SIGNAL"
        learning_status = "LEARNING_SIGNAL_AVAILABLE"
        learning_strength = "MODERATE"
        learning_ready = True

    elif observed_signal == "DELAY_ERROR_SIGNAL":
        signal_type = "DELAY_ERROR_OUTCOME_SIGNAL"
        learning_status = "LEARNING_SIGNAL_AVAILABLE"
        learning_strength = "LIMITED"
        learning_ready = True

    else:
        signal_type = "INSUFFICIENT_OUTCOME_SIGNAL"
        learning_status = "INSUFFICIENT_EVIDENCE"
        learning_strength = "NONE"
        learning_ready = False

    if (
        shipment_link
        and causal_effect
        and context["recommendation_weight_update_ready"]
    ):
        update_status = (
            "READY_FOR_RECOMMENDATION_WEIGHT_UPDATE"
        )

    elif learning_ready:
        update_status = (
            "LEARNING_SIGNAL_AVAILABLE_BUT_UPDATE_BLOCKED"
        )

    else:
        update_status = (
            "WAITING_FOR_VALID_LEARNING_SIGNAL"
        )

    return {
        "signal_type": signal_type,
        "learning_status": learning_status,
        "learning_strength": learning_strength,
        "learning_ready": learning_ready,
        "recommendation_update_status": update_status,
    }


def build_learning_signal(data):
    context = extract_context(data)

    signal = determine_learning_signal(context)

    return {
        "system": "SupplyPrescript",
        "module": "AI Recommendation Learning Signal Engine",
        "engine_version": "1.1",
        "status": "COMPLETED",
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "decision": {
            "decision_id": context["decision_id"],
            "selected_action": context["selected_action"],
            "decision_source": context["decision_source"],
        },

        "ai_recommendation": {
            "recommended_action": context["recommended_action"],
            "recommendation_rank": context["recommendation_rank"],
            "recommendation_score": context["recommendation_score"],
        },

        "outcome_reference": {
            "shipment_id": context["shipment_id"],
            "shipment_specific_decision_link": (
                context["shipment_specific_decision_link"]
            ),
        },

        "prediction_outcome": {
            "predicted_status": context["predicted_status"],
            "actual_status": context["actual_status"],
            "classification_correct": (
                context["classification_correct"]
            ),
            "predicted_delay_days": (
                context["predicted_delay_days"]
            ),
            "actual_delay_days": (
                context["actual_delay_days"]
            ),
            "absolute_delay_error_days": (
                context["absolute_delay_error_days"]
            ),
        },

        "learning_signal": {
            "signal_type": signal["signal_type"],
            "learning_status": signal["learning_status"],
            "learning_strength": signal["learning_strength"],
            "learning_ready": signal["learning_ready"],
        },

        "recommendation_learning": {
            "manager_action_recorded": (
                context["manager_action_recorded"]
            ),
            "actual_outcome_recorded": (
                context["actual_outcome_recorded"]
            ),
            "recommendation_evaluation_available": (
                context["recommendation_evaluation_available"]
            ),
            "causal_effect_established": (
                context["causal_effect_established"]
            ),
            "shipment_specific_link_available": (
                context["shipment_specific_decision_link"]
            ),
            "recommendation_update_status": (
                signal["recommendation_update_status"]
            ),
        },

        "learning_interpretation": {
            "signal_can_be_used_for_monitoring": (
                signal["learning_ready"]
            ),
            "signal_can_update_recommendation_weights": (
                signal["recommendation_update_status"]
                == "READY_FOR_RECOMMENDATION_WEIGHT_UPDATE"
            ),
            "additional_shipment_specific_outcomes_required": (
                not context["shipment_specific_decision_link"]
            ),
            "causal_claim_allowed": (
                context["causal_effect_established"]
            ),
        },

        "operational_safety": {
            "recommendation_weights_modified": False,
            "model_weights_modified": False,
            "models_retrained": False,
            "predictions_modified": False,
            "recommendation_report_modified": False,
            "manager_decision_modified": False,
            "shipments_modified": False,
            "database_modified": False,
            "business_decision_executed": False,
        },
    }


def save_learning_signal(data):
    print()
    print("Saving recommendation learning signal...")

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print("   ✓ Learning signal report saved.")


def print_report(data):
    decision = data["decision"]
    recommendation = data["ai_recommendation"]
    outcome = data["prediction_outcome"]
    learning = data["learning_signal"]
    recommendation_learning = data["recommendation_learning"]

    print()
    print("=" * 90)
    print("RECOMMENDATION LEARNING SIGNAL")
    print("-" * 90)

    print(f"Decision ID: {decision['decision_id']}")
    print(f"Selected Action: {decision['selected_action']}")
    print(
        f"Recommended Action: "
        f"{recommendation['recommended_action']}"
    )

    print()
    print("OUTCOME")
    print("-" * 90)
    print(
        f"Shipment Reference: "
        f"{data['outcome_reference']['shipment_id']}"
    )
    print(
        f"Predicted Status: "
        f"{outcome['predicted_status']}"
    )
    print(
        f"Actual Status: "
        f"{outcome['actual_status']}"
    )
    print(
        f"Classification Correct: "
        f"{outcome['classification_correct']}"
    )
    print(
        f"Predicted Delay: "
        f"{outcome['predicted_delay_days']} days"
    )
    print(
        f"Actual Delay: "
        f"{outcome['actual_delay_days']} days"
    )
    print(
        f"Absolute Delay Error: "
        f"{outcome['absolute_delay_error_days']} days"
    )

    print()
    print("LEARNING SIGNAL")
    print("-" * 90)
    print(f"Signal Type: {learning['signal_type']}")
    print(f"Learning Status: {learning['learning_status']}")
    print(f"Learning Strength: {learning['learning_strength']}")
    print(f"Learning Ready: {learning['learning_ready']}")

    print()
    print("RECOMMENDATION LEARNING")
    print("-" * 90)
    print(
        f"Manager Action Recorded: "
        f"{recommendation_learning['manager_action_recorded']}"
    )
    print(
        f"Actual Outcome Recorded: "
        f"{recommendation_learning['actual_outcome_recorded']}"
    )
    print(
        f"Recommendation Evaluation Available: "
        f"{recommendation_learning['recommendation_evaluation_available']}"
    )
    print(
        f"Causal Effect Established: "
        f"{recommendation_learning['causal_effect_established']}"
    )
    print(
        f"Shipment-Specific Link Available: "
        f"{recommendation_learning['shipment_specific_link_available']}"
    )
    print(
        f"Recommendation Update Status: "
        f"{recommendation_learning['recommendation_update_status']}"
    )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)
    print("Recommendation Weights Modified: NO")
    print("Model Weights Modified: NO")
    print("Models Retrained: NO")
    print("Business Decision Executed: NO")


def main():
    print("=" * 90)
    print("SUPPLYPRESCRIPT - AI RECOMMENDATION LEARNING SIGNAL ENGINE")
    print("=" * 90)

    try:
        analysis = load_analysis()

        print()
        print("Extracting recommendation and outcome context...")
        learning_signal = build_learning_signal(analysis)
        print("   ✓ Recommendation and outcome context extracted.")

        print_report(learning_signal)

        save_learning_signal(learning_signal)

        print()
        print("=" * 90)
        print("AI RECOMMENDATION LEARNING SIGNAL ENGINE COMPLETED")
        print("=" * 90)
        print(f"Report saved: {OUTPUT_FILE}")
        print("=" * 90)

    except Exception as error:
        print()
        print("✗ Recommendation learning signal engine failed.")
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()