"""
SupplyPrescript - AI Recommendation Outcome Analysis Engine

Purpose:
    Analyze the relationship between:
        1. AI recommendation
        2. Manager-selected action
        3. Prediction outcome
        4. Actual shipment outcome

Important:
    This engine evaluates decision evidence.

    It does NOT claim that a manager action caused or prevented
    the observed shipment outcome because the current data does not
    contain a causal experiment or counterfactual outcome.

Safety:
    - Does not execute recommendations.
    - Does not modify shipments.
    - Does not modify suppliers.
    - Does not modify inventory.
    - Does not modify optimization.
    - Does not modify models.
    - Does not trigger retraining.
    - Does not modify the database.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path.cwd()

FEEDBACK_DIR = BASE_DIR / "ai_engine" / "feedback"

INPUT_FILE = (
    FEEDBACK_DIR / "decision_outcomes.json"
)

OUTPUT_FILE = (
    FEEDBACK_DIR / "recommendation_outcome_analysis.json"
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
    """Save JSON data."""

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


def normalize_action(action: Any) -> str:
    """Normalize an action name."""

    if action is None:
        return ""

    return (
        str(action)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def compare_actions(
    recommended_action: Any,
    selected_action: Any,
) -> bool | None:
    """Determine whether the manager selected the AI recommendation."""

    if (
        recommended_action is None
        or selected_action is None
    ):
        return None

    recommended = normalize_action(
        recommended_action
    )

    selected = normalize_action(
        selected_action
    )

    if not recommended or not selected:
        return None

    return recommended == selected


def calculate_outcome_signal(
    classification_correct: Any,
    delay_error: Any,
) -> str:
    """Classify the available outcome evidence."""

    if classification_correct is False:
        return "NEGATIVE_PREDICTION_SIGNAL"

    if classification_correct is True:
        if delay_error is not None:
            return "PREDICTION_CORRECT_WITH_DELAY_ERROR"

        return "POSITIVE_PREDICTION_SIGNAL"

    if delay_error is not None:
        return "DELAY_ERROR_SIGNAL"

    return "INSUFFICIENT_OUTCOME_EVIDENCE"


def calculate_recommendation_alignment(
    action_match: bool | None,
) -> str:
    """Describe recommendation and manager-action alignment."""

    if action_match is True:
        return "ALIGNED"

    if action_match is False:
        return "MANAGER_SELECTED_ALTERNATIVE"

    return "NOT_AVAILABLE"


def build_analysis(
    decision_outcome: dict[str, Any],
) -> dict[str, Any]:
    """Build the recommendation outcome analysis."""

    decision = decision_outcome.get(
        "decision",
        {},
    )

    recommendation = decision_outcome.get(
        "ai_recommendation",
        {},
    )

    comparison = decision_outcome.get(
        "prediction_vs_actual",
        {},
    )

    outcome_assessment = decision_outcome.get(
        "outcome_assessment",
        {},
    )

    linkage = decision_outcome.get(
        "outcome_linkage",
        {},
    )

    learning = decision_outcome.get(
        "closed_loop_learning",
        {},
    )

    if not isinstance(decision, dict):
        decision = {}

    if not isinstance(recommendation, dict):
        recommendation = {}

    if not isinstance(comparison, dict):
        comparison = {}

    if not isinstance(outcome_assessment, dict):
        outcome_assessment = {}

    if not isinstance(linkage, dict):
        linkage = {}

    if not isinstance(learning, dict):
        learning = {}

    recommended_action = recommendation.get(
        "action"
    )

    selected_action = decision.get(
        "selected_action"
    )

    action_match = compare_actions(
        recommended_action,
        selected_action,
    )

    classification_correct = comparison.get(
        "classification_correct"
    )

    delay_error = comparison.get(
        "absolute_delay_error_days"
    )

    outcome_signal = calculate_outcome_signal(
        classification_correct,
        delay_error,
    )

    alignment = calculate_recommendation_alignment(
        action_match
    )

    shipment_specific_link = linkage.get(
        "shipment_specific_decision_link",
        False,
    )

    evaluation_available = (
        comparison.get(
            "classification_correct"
        )
        is not None
        or comparison.get(
            "absolute_delay_error_days"
        )
        is not None
    )

    return {
        "system": "SupplyPrescript",
        "module": (
            "AI Recommendation Outcome Analysis Engine"
        ),
        "engine_version": "1.0",
        "status": "COMPLETED",
        "analyzed_at": datetime.now().isoformat(),

        "decision_reference": {
            "decision_id": decision.get(
                "decision_id"
            ),
            "selected_action": selected_action,
            "decision_status": decision.get(
                "decision_status"
            ),
            "decision_source": decision.get(
                "decision_source"
            ),
        },

        "recommendation_reference": {
            "recommended_action": recommended_action,
            "recommendation_rank": recommendation.get(
                "rank"
            ),
            "recommendation_score": recommendation.get(
                "score"
            ),
            "recommendation_reasons": recommendation.get(
                "reasons",
                [],
            ),
        },

        "recommendation_alignment": {
            "manager_selected_ai_recommendation": (
                action_match
            ),
            "alignment_status": alignment,
        },

        "outcome_evidence": {
            "shipment_id": linkage.get(
                "shipment_id"
            ),
            "predicted_status": comparison.get(
                "predicted_status"
            ),
            "actual_status": comparison.get(
                "actual_status"
            ),
            "classification_correct": (
                classification_correct
            ),
            "predicted_delay_days": comparison.get(
                "predicted_delay_days"
            ),
            "actual_delay_days": comparison.get(
                "actual_delay_days"
            ),
            "absolute_delay_error_days": (
                delay_error
            ),
            "outcome_assessment": (
                outcome_assessment.get(
                    "assessment"
                )
            ),
        },

        "recommendation_effectiveness": {
            "outcome_evaluation_available": (
                evaluation_available
            ),
            "observed_outcome_signal": (
                outcome_signal
            ),
            "recommendation_effectiveness_status": (
                "EVIDENCE_AVAILABLE"
                if evaluation_available
                else "INSUFFICIENT_EVIDENCE"
            ),
            "causal_effect_established": False,
            "causal_effect_reason": (
                "The current dataset contains one observed "
                "outcome reference but does not contain a "
                "counterfactual or controlled comparison."
            ),
        },

        "closed_loop_learning": {
            "manager_action_recorded": learning.get(
                "manager_action_recorded",
                False,
            ),
            "actual_outcome_recorded": learning.get(
                "actual_outcome_recorded",
                False,
            ),
            "prediction_evaluation_available": (
                learning.get(
                    "prediction_evaluation_available",
                    False,
                )
            ),
            "learning_signal_available": (
                learning.get(
                    "learning_signal_available",
                    False,
                )
            ),
            "recommendation_evaluation_available": (
                evaluation_available
            ),
            "recommendation_weight_update_ready": (
                evaluation_available
                and shipment_specific_link
            ),
        },

        "limitations": [
            (
                "The manager decision does not currently "
                "contain a shipment_id."
            ),
            (
                "The selected outcome is therefore an "
                "outcome reference rather than a verified "
                "shipment-specific decision outcome."
            ),
            (
                "The current data does not establish causal "
                "impact of the selected action."
            ),
            (
                "Recommendation effectiveness should be "
                "evaluated across multiple decision-outcome "
                "records before changing recommendation weights."
            ),
        ],

        "operational_safety": {
            "recommendation_executed": False,
            "shipments_modified": False,
            "supplier_modified": False,
            "inventory_modified": False,
            "optimization_executed": False,
            "prediction_outputs_modified": False,
            "risk_reports_modified": False,
            "manager_decision_modified": False,
            "models_modified": False,
            "retraining_triggered": False,
            "recommendation_weights_modified": False,
            "database_modified": False,
            "business_decision_executed": False,
        },
    }


def main() -> None:
    """Run recommendation outcome analysis."""

    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI RECOMMENDATION "
        "OUTCOME ANALYSIS ENGINE"
    )
    print("=" * 90)

    print()
    print("Loading decision outcome record...")

    decision_outcome = load_json(
        INPUT_FILE
    )

    print(
        "   ✓ Decision outcome record loaded."
    )

    print()
    print("Analyzing recommendation alignment...")

    analysis = build_analysis(
        decision_outcome
    )

    print(
        "   ✓ Recommendation analysis completed."
    )

    decision = analysis[
        "decision_reference"
    ]

    recommendation = analysis[
        "recommendation_reference"
    ]

    alignment = analysis[
        "recommendation_alignment"
    ]

    outcome = analysis[
        "outcome_evidence"
    ]

    effectiveness = analysis[
        "recommendation_effectiveness"
    ]

    learning = analysis[
        "closed_loop_learning"
    ]

    print()
    print("DECISION")
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
        f"Decision Source: "
        f"{decision['decision_source']}"
    )

    print()
    print("AI RECOMMENDATION")
    print("-" * 90)

    print(
        f"Recommended Action: "
        f"{recommendation['recommended_action']}"
    )

    print(
        f"Recommendation Rank: "
        f"{recommendation['recommendation_rank']}"
    )

    print(
        f"Recommendation Score: "
        f"{recommendation['recommendation_score']}"
    )

    print()
    print("RECOMMENDATION ALIGNMENT")
    print("-" * 90)

    print(
        "Manager Selected AI Recommendation: "
        f"{'YES' if alignment['manager_selected_ai_recommendation'] else 'NO'}"
    )

    print(
        f"Alignment Status: "
        f"{alignment['alignment_status']}"
    )

    print()
    print("OUTCOME EVIDENCE")
    print("-" * 90)

    print(
        f"Shipment Reference: "
        f"{outcome['shipment_id']}"
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
    print("RECOMMENDATION EFFECTIVENESS")
    print("-" * 90)

    print(
        "Outcome Evaluation Available: "
        f"{'YES' if effectiveness['outcome_evaluation_available'] else 'NO'}"
    )

    print(
        f"Observed Outcome Signal: "
        f"{effectiveness['observed_outcome_signal']}"
    )

    print(
        f"Effectiveness Status: "
        f"{effectiveness['recommendation_effectiveness_status']}"
    )

    print(
        "Causal Effect Established: "
        f"{'YES' if effectiveness['causal_effect_established'] else 'NO'}"
    )

    print()
    print("CLOSED-LOOP LEARNING")
    print("-" * 90)

    print(
        "Manager Action Recorded: "
        f"{'YES' if learning['manager_action_recorded'] else 'NO'}"
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
        "Recommendation Evaluation Available: "
        f"{'YES' if learning['recommendation_evaluation_available'] else 'NO'}"
    )

    print(
        "Recommendation Weight Update Ready: "
        f"{'YES' if learning['recommendation_weight_update_ready'] else 'NO'}"
    )

    print()
    print("Saving recommendation outcome analysis...")

    save_json(
        OUTPUT_FILE,
        analysis,
    )

    print(
        "   ✓ Analysis report saved."
    )

    print()
    print("=" * 90)
    print(
        "AI RECOMMENDATION OUTCOME ANALYSIS "
        "COMPLETED"
    )
    print("=" * 90)

    print(
        f"Report saved: {OUTPUT_FILE}"
    )

    print("=" * 90)


if __name__ == "__main__":
    main()
    