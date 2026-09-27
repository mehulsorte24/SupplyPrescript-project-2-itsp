"""
SupplyPrescript - Manager Decision Outcome Tracking Engine

Purpose:
    Connect a captured manager decision with an evaluated shipment outcome
    and create a closed-loop learning record.

The current manager decision structure contains:
    decision_context
    ai_recommendation
    manager_decision
    outcome_tracking
    learning_status
    operational_safety

Important:
    The manager decision currently does not contain a shipment_id.
    Therefore this engine does not invent a shipment-specific relationship.

Safety:
    - Does not modify shipments.
    - Does not modify suppliers.
    - Does not modify inventory.
    - Does not execute optimization.
    - Does not modify models.
    - Does not trigger retraining.
    - Does not modify the database.
    - Does not execute the manager's decision.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path.cwd()

PREDICTION_DIR = BASE_DIR / "ai_engine" / "prediction"
FEEDBACK_DIR = BASE_DIR / "ai_engine" / "feedback"

MANAGER_DECISION_FILE = (
    PREDICTION_DIR / "manager_decision.json"
)

PREDICTION_OUTCOMES_FILE = (
    FEEDBACK_DIR / "prediction_outcomes.json"
)

OUTPUT_FILE = (
    FEEDBACK_DIR / "decision_outcomes.json"
)


def load_json(file_path: Path) -> Any:
    """Load JSON data from a file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_json(
    file_path: Path,
    data: Any,
) -> None:
    """Save JSON data using readable formatting."""

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def calculate_learning_signal(
    classification_correct: bool | None,
    delay_error: float | None,
) -> bool:
    """Determine whether an evaluation signal is available."""

    return (
        classification_correct is not None
        or delay_error is not None
    )


def calculate_outcome_assessment(
    classification_correct: bool | None,
    delay_error: float | None,
) -> str:
    """Create a factual outcome assessment."""

    if classification_correct is False:
        return "PREDICTION_CLASSIFICATION_MISMATCH"

    if classification_correct is True:
        if delay_error is not None:
            return (
                "PREDICTION_CLASSIFICATION_CORRECT_WITH_DELAY_ERROR"
            )

        return "PREDICTION_CLASSIFICATION_CORRECT"

    if delay_error is not None:
        return (
            "DELAY_ERROR_AVAILABLE_WITHOUT_CLASSIFICATION_RESULT"
        )

    return "OUTCOME_INFORMATION_INCOMPLETE"


def build_decision_outcome_record(
    manager_decision: dict[str, Any],
    evaluated_record: dict[str, Any],
) -> dict[str, Any]:
    """Build the complete closed-loop decision outcome record."""

    decision_context = manager_decision.get(
        "decision_context",
        {},
    )

    ai_recommendation = manager_decision.get(
        "ai_recommendation",
        {},
    )

    manager_choice = manager_decision.get(
        "manager_decision",
        {},
    )

    outcome_tracking = manager_decision.get(
        "outcome_tracking",
        {},
    )

    learning_status = manager_decision.get(
        "learning_status",
        {},
    )

    if not isinstance(decision_context, dict):
        decision_context = {}

    if not isinstance(ai_recommendation, dict):
        ai_recommendation = {}

    if not isinstance(manager_choice, dict):
        manager_choice = {}

    if not isinstance(outcome_tracking, dict):
        outcome_tracking = {}

    if not isinstance(learning_status, dict):
        learning_status = {}

    shipment_id = evaluated_record.get(
        "shipment_id"
    )

    prediction = evaluated_record.get(
        "prediction",
        {},
    )

    actual = evaluated_record.get(
        "actual",
        {},
    )

    evaluation = evaluated_record.get(
        "evaluation",
        {},
    )

    if not isinstance(prediction, dict):
        prediction = {}

    if not isinstance(actual, dict):
        actual = {}

    if not isinstance(evaluation, dict):
        evaluation = {}

    predicted_status = prediction.get(
        "status"
    )

    predicted_delay_days = prediction.get(
        "delay_days"
    )

    actual_status = actual.get(
        "status"
    )

    actual_delay_days = actual.get(
        "delay_days"
    )

    classification_correct = evaluation.get(
        "classification_correct"
    )

    absolute_delay_error_days = evaluation.get(
        "absolute_delay_error_days"
    )

    learning_signal_available = calculate_learning_signal(
        classification_correct,
        absolute_delay_error_days,
    )

    outcome_assessment = calculate_outcome_assessment(
        classification_correct,
        absolute_delay_error_days,
    )

    return {
        "system": "SupplyPrescript",
        "module": (
            "AI Manager Decision Outcome Tracking Engine"
        ),
        "engine_version": "1.2",
        "status": "COMPLETED",
        "recorded_at": datetime.now().isoformat(),

        "decision": {
            "decision_id": manager_decision.get(
                "decision_id"
            ),
            "decision_status": manager_decision.get(
                "decision_status"
            ),
            "decision_timestamp": manager_decision.get(
                "decision_timestamp"
            ),
            "selected_action": manager_choice.get(
                "selected_action"
            ),
            "decision_rationale": manager_choice.get(
                "rationale"
            ),
            "decision_source": manager_choice.get(
                "decision_source"
            ),
        },

        "ai_recommendation": {
            "rank": ai_recommendation.get(
                "rank"
            ),
            "action": ai_recommendation.get(
                "action"
            ),
            "score": ai_recommendation.get(
                "score"
            ),
            "reasons": ai_recommendation.get(
                "reasons",
                [],
            ),
        },

        "decision_context": {
            "risk_level": decision_context.get(
                "risk_level"
            ),
            "risk_exposure": decision_context.get(
                "risk_exposure"
            ),
            "delay_probability": decision_context.get(
                "delay_probability"
            ),
            "expected_delay_days": decision_context.get(
                "expected_delay_days"
            ),
            "recommendation_urgency": decision_context.get(
                "recommendation_urgency"
            ),
        },

        "outcome_linkage": {
            "shipment_id": shipment_id,
            "linkage_method": (
                "EVALUATED_OUTCOME_REFERENCE"
            ),
            "decision_shipment_id_available": False,
            "shipment_specific_decision_link": False,
            "linkage_warning": (
                "The manager decision does not currently "
                "contain a shipment_id. The evaluated shipment "
                "is therefore stored as an outcome reference "
                "and is not claimed to be the shipment affected "
                "by the manager decision."
            ),
        },

        "prediction_vs_actual": {
            "predicted_status": predicted_status,
            "actual_status": actual_status,
            "classification_correct": (
                classification_correct
            ),
            "predicted_delay_days": (
                predicted_delay_days
            ),
            "actual_delay_days": (
                actual_delay_days
            ),
            "absolute_delay_error_days": (
                absolute_delay_error_days
            ),
        },

        "outcome_assessment": {
            "assessment": outcome_assessment,
            "learning_signal_available": (
                learning_signal_available
            ),
        },

        "previous_decision_tracking_state": {
            "outcome_available": outcome_tracking.get(
                "outcome_available"
            ),
            "actual_delay_days": outcome_tracking.get(
                "actual_delay_days"
            ),
            "actual_status": outcome_tracking.get(
                "actual_status"
            ),
            "outcome_recorded": outcome_tracking.get(
                "outcome_recorded"
            ),
        },

        "previous_learning_state": {
            "prediction_evaluated": learning_status.get(
                "prediction_evaluated"
            ),
            "recommendation_evaluated": learning_status.get(
                "recommendation_evaluated"
            ),
            "feedback_available": learning_status.get(
                "feedback_available"
            ),
            "model_update_required": learning_status.get(
                "model_update_required"
            ),
        },

        "closed_loop_learning": {
            "manager_action_recorded": (
                manager_choice.get(
                    "selected_action"
                )
                is not None
            ),
            "manager_rationale_recorded": (
                bool(
                    str(
                        manager_choice.get(
                            "rationale",
                            ""
                        )
                    ).strip()
                )
            ),
            "actual_outcome_recorded": (
                actual_status is not None
                or actual_delay_days is not None
            ),
            "prediction_evaluation_available": (
                classification_correct is not None
                or absolute_delay_error_days is not None
            ),
            "learning_signal_available": (
                learning_signal_available
            ),
            "recommendation_effectiveness_evaluated": False,
            "model_weights_modified": False,
            "model_retrained": False,
        },

        "operational_safety": {
            "prediction_outputs_modified": False,
            "recommendation_report_modified": False,
            "manager_decision_modified": False,
            "shipments_modified": False,
            "supplier_modified": False,
            "inventory_modified": False,
            "optimization_executed": False,
            "models_modified": False,
            "retraining_triggered": False,
            "database_modified": False,
            "business_decision_executed": False,
        },
    }


def main() -> None:
    """Run the manager decision outcome tracking engine."""

    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI MANAGER DECISION "
        "OUTCOME TRACKING ENGINE"
    )
    print("=" * 90)

    print()
    print("Loading manager decision...")

    manager_decision = load_json(
        MANAGER_DECISION_FILE
    )

    print(
        "   ✓ Manager decision loaded."
    )

    print()
    print("Loading evaluated prediction outcomes...")

    prediction_outcomes = load_json(
        PREDICTION_OUTCOMES_FILE
    )

    evaluated_predictions = prediction_outcomes.get(
        "evaluated_predictions",
        [],
    )

    if not isinstance(
        evaluated_predictions,
        list,
    ):
        raise ValueError(
            "The 'evaluated_predictions' field "
            "is not a list."
        )

    if not evaluated_predictions:
        raise ValueError(
            "No evaluated prediction records were found."
        )

    print(
        f"   ✓ {len(evaluated_predictions)} evaluated "
        "outcome record(s) available."
    )

    print()
    print("Selecting evaluated outcome reference...")

    evaluated_record = evaluated_predictions[0]

    if not isinstance(
        evaluated_record,
        dict,
    ):
        raise ValueError(
            "The selected evaluated outcome "
            "is not a valid record."
        )

    shipment_id = evaluated_record.get(
        "shipment_id",
        "N/A",
    )

    print(
        f"   ✓ Outcome reference selected: {shipment_id}"
    )

    print()
    print(
        "Building closed-loop decision "
        "outcome record..."
    )

    decision_outcome = build_decision_outcome_record(
        manager_decision,
        evaluated_record,
    )

    print(
        "   ✓ Decision outcome record built."
    )

    decision = decision_outcome[
        "decision"
    ]

    context = decision_outcome[
        "decision_context"
    ]

    recommendation = decision_outcome[
        "ai_recommendation"
    ]

    linkage = decision_outcome[
        "outcome_linkage"
    ]

    comparison = decision_outcome[
        "prediction_vs_actual"
    ]

    assessment = decision_outcome[
        "outcome_assessment"
    ]

    learning = decision_outcome[
        "closed_loop_learning"
    ]

    print()
    print("DECISION OUTCOME")
    print("-" * 90)

    print(
        f"Decision ID: "
        f"{decision['decision_id']}"
    )

    print(
        f"Selected Action: "
        f"{decision['selected_action']}"
    )

    print(
        f"Decision Status: "
        f"{decision['decision_status']}"
    )

    print(
        f"Decision Source: "
        f"{decision['decision_source']}"
    )

    print(
        f"Decision Rationale: "
        f"{decision['decision_rationale']}"
    )

    print()
    print("AI RECOMMENDATION")
    print("-" * 90)

    print(
        f"Recommended Action: "
        f"{recommendation['action']}"
    )

    print(
        f"Recommendation Rank: "
        f"{recommendation['rank']}"
    )

    print(
        f"Recommendation Score: "
        f"{recommendation['score']}"
    )

    print()
    print("DECISION CONTEXT")
    print("-" * 90)

    print(
        f"Risk Level: "
        f"{context['risk_level']}"
    )

    print(
        f"Risk Exposure: "
        f"{context['risk_exposure']}"
    )

    print(
        f"Delay Probability: "
        f"{context['delay_probability']}"
    )

    print(
        f"Expected Delay: "
        f"{context['expected_delay_days']} days"
    )

    print(
        f"Recommendation Urgency: "
        f"{context['recommendation_urgency']}"
    )

    print()
    print("OUTCOME LINKAGE")
    print("-" * 90)

    print(
        f"Outcome Shipment: "
        f"{linkage['shipment_id']}"
    )

    print(
        "Decision Shipment ID Available: "
        f"{'YES' if linkage['decision_shipment_id_available'] else 'NO'}"
    )

    print(
        "Shipment-Specific Decision Link: "
        f"{'YES' if linkage['shipment_specific_decision_link'] else 'NO'}"
    )

    print()
    print("PREDICTION VS ACTUAL")
    print("-" * 90)

    print(
        f"Predicted Status: "
        f"{comparison['predicted_status']}"
    )

    print(
        f"Actual Status: "
        f"{comparison['actual_status']}"
    )

    print(
        "Classification Correct: "
        f"{comparison['classification_correct']}"
    )

    print(
        f"Predicted Delay: "
        f"{comparison['predicted_delay_days']} days"
    )

    print(
        f"Actual Delay: "
        f"{comparison['actual_delay_days']} days"
    )

    print(
        f"Absolute Delay Error: "
        f"{comparison['absolute_delay_error_days']} days"
    )

    print()
    print("CLOSED-LOOP LEARNING")
    print("-" * 90)

    print(
        "Manager Action Recorded: "
        f"{'YES' if learning['manager_action_recorded'] else 'NO'}"
    )

    print(
        "Manager Rationale Recorded: "
        f"{'YES' if learning['manager_rationale_recorded'] else 'NO'}"
    )

    print(
        "Actual Outcome Recorded: "
        f"{'YES' if learning['actual_outcome_recorded'] else 'NO'}"
    )

    print(
        "Prediction Evaluation Available: "
        f"{'YES' if learning['prediction_evaluation_available'] else 'NO'}"
    )

    print(
        "Learning Signal Available: "
        f"{'YES' if learning['learning_signal_available'] else 'NO'}"
    )

    print()
    print("OUTCOME ASSESSMENT")
    print("-" * 90)

    print(
        f"Assessment: "
        f"{assessment['assessment']}"
    )

    print(
        "Learning Signal: "
        f"{'AVAILABLE' if assessment['learning_signal_available'] else 'NOT AVAILABLE'}"
    )

    print()
    print("Saving decision outcome...")

    save_json(
        OUTPUT_FILE,
        decision_outcome,
    )

    print(
        "   ✓ Decision outcome saved."
    )

    print()
    print("=" * 90)
    print(
        "MANAGER DECISION OUTCOME TRACKING "
        "COMPLETED"
    )
    print("=" * 90)

    print(
        f"Decision outcome saved: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 90)


if __name__ == "__main__":
    main()