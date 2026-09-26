import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path.cwd()

RECOMMENDATION_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "action_recommendation_report.json"
)

DECISION_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "manager_decision.json"
)


ACTION_NAME_MAP = {
    1: "Expedite transportation",
    2: "Evaluate alternate supplier",
    3: "Increase inventory buffer",
    4: "Prioritize critical shipments",
    5: "Increase monitoring frequency",
}


def load_recommendations():
    """Load the AI action recommendation report."""

    if not RECOMMENDATION_FILE.exists():
        raise FileNotFoundError(
            f"Recommendation report not found:\n{RECOMMENDATION_FILE}"
        )

    with RECOMMENDATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def find_action_list(data):
    """Recursively locate the recommendation action list."""

    if isinstance(data, dict):

        preferred_keys = [
            "ranked_mitigation_options",
            "mitigation_options",
            "candidate_actions",
            "recommended_actions",
            "actions",
            "recommendations",
        ]

        for key in preferred_keys:

            value = data.get(key)

            if isinstance(value, list) and value:
                return value

        for value in data.values():

            result = find_action_list(value)

            if result:
                return result

    elif isinstance(data, list):

        if data:

            action_like_items = 0

            for item in data:

                if isinstance(item, dict):

                    action_name = (
                        item.get("action")
                        or item.get("name")
                        or item.get("title")
                        or item.get("recommendation")
                    )

                    if action_name:
                        action_like_items += 1

                elif isinstance(item, str):

                    action_like_items += 1

            if action_like_items > 0:
                return data

        for item in data:

            result = find_action_list(item)

            if result:
                return result

    return []


def find_value(data, keys, default=None):
    """Recursively find the first matching value."""

    if isinstance(data, dict):

        for key in keys:

            if key in data:
                return data[key]

        for value in data.values():

            result = find_value(
                value,
                keys,
                None,
            )

            if result is not None:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_value(
                item,
                keys,
                None,
            )

            if result is not None:
                return result

    return default


def normalize_probability(value):
    """
    Normalize probability values.

    Supports:
    0.7185  -> 71.85
    71.85   -> 71.85
    """

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    if 0 <= numeric_value <= 1:
        return numeric_value * 100

    return numeric_value


def normalize_risk_exposure(value):
    """
    Normalize risk exposure.

    Supports:
    0.7537 -> 75.37
    75.37  -> 75.37
    """

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    if 0 <= numeric_value <= 1:
        return numeric_value * 100

    return numeric_value


def extract_decision_context(report):
    """Extract decision context from the recommendation report."""

    risk_level = find_value(
        report,
        [
            "risk_level",
            "overall_risk_level",
        ],
        "UNKNOWN",
    )

    risk_exposure = find_value(
        report,
        [
            "risk_exposure",
            "risk_exposure_score",
        ],
        0,
    )

    delay_probability = find_value(
        report,
        [
            "delay_probability",
            "average_delay_probability",
        ],
        0,
    )

    expected_delay_days = find_value(
        report,
        [
            "expected_delay_days",
            "average_expected_delay_days",
        ],
        0,
    )

    urgency = find_value(
        report,
        [
            "recommendation_urgency",
            "urgency",
        ],
        "UNKNOWN",
    )

    actions = find_action_list(report)

    return {
        "risk_level": risk_level,
        "risk_exposure": normalize_risk_exposure(
            risk_exposure
        ),
        "delay_probability": normalize_probability(
            delay_probability
        ),
        "expected_delay_days": expected_delay_days,
        "recommendation_urgency": urgency,
        "actions": actions,
    }


def extract_reason(action):
    """Extract recommendation reasoning."""

    reasons = (
        action.get("reasons")
        or action.get("reason")
        or action.get("rationale")
        or []
    )

    if isinstance(reasons, str):
        return [reasons]

    if isinstance(reasons, list):
        return reasons

    return []


def normalize_actions(actions):
    """Normalize recommendation actions."""

    normalized = []

    for index, action in enumerate(
        actions,
        start=1,
    ):

        if isinstance(action, str):

            action_name = action

            normalized.append(
                {
                    "rank": index,
                    "action": action_name,
                    "score": None,
                    "reasons": [],
                }
            )

            continue

        if not isinstance(action, dict):
            continue

        rank = action.get(
            "rank",
            index,
        )

        try:
            rank = int(rank)
        except (TypeError, ValueError):
            rank = index

        action_name = (
            action.get("action")
            or action.get("name")
            or action.get("title")
            or action.get("recommendation")
        )

        if (
            not action_name
            or str(action_name).strip().lower()
            in {
                "action 1",
                "action 2",
                "action 3",
                "action 4",
                "action 5",
            }
        ):

            action_name = ACTION_NAME_MAP.get(
                rank,
                f"Action {rank}",
            )

        score = (
            action.get("score")
            if action.get("score") is not None
            else action.get("relevance_score")
        )

        reasons = extract_reason(action)

        normalized.append(
            {
                "rank": rank,
                "action": action_name,
                "score": score,
                "reasons": reasons,
            }
        )

    return normalized


def display_actions(actions):
    """Display available AI-generated actions."""

    print()
    print("AVAILABLE AI-GENERATED ACTIONS")
    print("-" * 90)

    for index, action in enumerate(
        actions,
        start=1,
    ):

        score = action.get("score")

        score_text = (
            f"{score}"
            if score is not None
            else "N/A"
        )

        print(
            f"{index:02d}. {action['action']} | "
            f"AI Score: {score_text}"
        )

        reasons = action.get(
            "reasons",
            [],
        )

        for reason in reasons:
            print(
                f"    Reason: {reason}"
            )

    print("-" * 90)


def capture_manager_selection(actions):
    """Capture the manager's selected action."""

    while True:

        selection = input(
            "Select an action number (or 0 to cancel): "
        ).strip()

        if not selection.isdigit():

            print(
                "Please enter a valid action number."
            )

            continue

        selection_number = int(selection)

        if selection_number == 0:
            return None

        if 1 <= selection_number <= len(actions):
            return actions[
                selection_number - 1
            ]

        print(
            f"Please select a number between "
            f"1 and {len(actions)}, or 0 to cancel."
        )


def capture_rationale():
    """Capture manager decision rationale."""

    print()
    print("MANAGER DECISION RATIONALE")
    print("-" * 90)

    rationale = input(
        "Why was this action selected? "
    ).strip()

    if not rationale:
        rationale = "No rationale provided."

    return rationale


def build_decision_record(
    context,
    selected_action,
    rationale,
):
    """Build the manager decision record."""

    decision_id = (
        "DEC-"
        + datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d%H%M%S"
        )
        + "-"
        + uuid4().hex[:6].upper()
    )

    decision_timestamp = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    return {
        "decision_engine": (
            "AI Manager Decision Capture Engine"
        ),
        "engine_version": "1.1",
        "decision_id": decision_id,
        "decision_status": "CAPTURED",
        "decision_timestamp": decision_timestamp,
        "decision_context": {
            "risk_level": context[
                "risk_level"
            ],
            "risk_exposure": context[
                "risk_exposure"
            ],
            "delay_probability": context[
                "delay_probability"
            ],
            "expected_delay_days": context[
                "expected_delay_days"
            ],
            "recommendation_urgency": context[
                "recommendation_urgency"
            ],
        },
        "ai_recommendation": {
            "rank": selected_action[
                "rank"
            ],
            "action": selected_action[
                "action"
            ],
            "score": selected_action[
                "score"
            ],
            "reasons": selected_action[
                "reasons"
            ],
        },
        "manager_decision": {
            "selected_action": selected_action[
                "action"
            ],
            "rationale": rationale,
            "decision_source": "MANAGER",
        },
        "outcome_tracking": {
            "outcome_available": False,
            "actual_delay_days": None,
            "actual_status": None,
            "outcome_recorded": False,
        },
        "learning_status": {
            "prediction_evaluated": False,
            "recommendation_evaluated": False,
            "feedback_available": False,
            "model_update_required": False,
        },
        "operational_safety": {
            "prediction_outputs_modified": False,
            "recommendation_report_modified": False,
            "shipments_modified": False,
            "supplier_modified": False,
            "inventory_modified": False,
            "optimization_executed": False,
            "database_modified": False,
            "business_decision_executed": False,
        },
    }


def save_decision(decision):
    """Save the manager decision."""

    DECISION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with DECISION_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            decision,
            file,
            indent=4,
        )


def main():

    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI MANAGER DECISION CAPTURE ENGINE"
    )
    print("=" * 90)

    print()
    print("Loading action recommendations...")

    try:

        recommendation_report = (
            load_recommendations()
        )

    except Exception as error:

        print(
            f"   ✗ Failed to load recommendations: "
            f"{error}"
        )

        return

    print(
        "   ✓ Action recommendation report loaded."
    )

    print()
    print("Extracting decision context...")

    context = extract_decision_context(
        recommendation_report
    )

    actions = normalize_actions(
        context["actions"]
    )

    if not actions:

        print(
            "   ✗ No recommendation actions available."
        )

        return

    print(
        f"   ✓ {len(actions)} candidate actions available."
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
        f"{context['risk_exposure']:.2f}%"
    )

    print(
        f"Delay Probability: "
        f"{context['delay_probability']:.2f}%"
    )

    print(
        f"Expected Delay: "
        f"{float(context['expected_delay_days']):.3f} days"
    )

    print(
        f"Recommendation Urgency: "
        f"{context['recommendation_urgency']}"
    )

    display_actions(actions)

    print()
    print("Capturing manager decision...")

    selected_action = (
        capture_manager_selection(
            actions
        )
    )

    if selected_action is None:

        print()
        print("Decision capture cancelled.")
        print(
            "No business action was executed."
        )

        return

    rationale = capture_rationale()

    print()
    print(
        "Building manager decision record..."
    )

    decision = build_decision_record(
        context=context,
        selected_action=selected_action,
        rationale=rationale,
    )

    print(
        "   ✓ Manager decision record built."
    )

    print()
    print("Saving manager decision...")

    save_decision(decision)

    print(
        "   ✓ Manager decision saved."
    )

    print()
    print("=" * 90)
    print("MANAGER DECISION CAPTURED")
    print("-" * 90)

    print(
        f"Decision ID: "
        f"{decision['decision_id']}"
    )

    print(
        f"Selected Action: "
        f"{decision['manager_decision']['selected_action']}"
    )

    print(
        f"Decision Status: "
        f"{decision['decision_status']}"
    )

    print(
        f"Decision Source: "
        f"{decision['manager_decision']['decision_source']}"
    )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)
    print(
        "Prediction Outputs Modified: NO"
    )
    print(
        "Recommendation Report Modified: NO"
    )
    print(
        "Shipments Modified: NO"
    )
    print(
        "Supplier Modified: NO"
    )
    print(
        "Inventory Modified: NO"
    )
    print(
        "Optimization Executed: NO"
    )
    print(
        "Database Modified: NO"
    )
    print(
        "Business Decision Executed: NO"
    )

    print()
    print("=" * 90)
    print(
        "AI manager decision capture completed successfully."
    )
    print(
        f"Decision saved: {DECISION_FILE}"
    )
    print("=" * 90)


if __name__ == "__main__":
    main()