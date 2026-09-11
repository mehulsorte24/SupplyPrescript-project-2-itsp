from pathlib import Path
import json
from datetime import datetime, timedelta


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRAINING_DECISION_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_decision_report.json"
)

RETRAINING_TRIGGER_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_trigger.json"
)

MODEL_VERSION_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "models"
    / "model_version.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_schedule.json"
)


# ============================================================
# SCHEDULER CONFIGURATION
# ============================================================

DEFAULT_COOLDOWN_HOURS = 24
DEFAULT_RETRAINING_WINDOW_HOURS = 6


# ============================================================
# FILE HELPERS
# ============================================================

def load_json_file(file_path: Path, label: str) -> dict:
    """Load a JSON file safely."""

    if not file_path.exists():
        print(f"   ! {label} not found:")
        print(f"     {file_path}")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        print(f"   ✓ {label} found.")
        return data

    except json.JSONDecodeError as error:
        print(f"   ✗ Failed to read {label}:")
        print(f"     {error}")
        return {}

    except OSError as error:
        print(f"   ✗ Failed to open {label}:")
        print(f"     {error}")
        return {}


def save_json_file(file_path: Path, data: dict) -> None:
    """Save scheduler output as formatted JSON."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print()
    print("✓ Retraining schedule saved:")
    print(f"  {file_path}")


# ============================================================
# EXTRACTION HELPERS
# ============================================================

def extract_model_version(
    decision_report: dict,
    version_report: dict,
) -> str:
    """Extract the most reliable available model version."""

    possible_versions = [
        decision_report.get("model_version"),
        decision_report.get("current_model_version"),
        version_report.get("current_version"),
        version_report.get("model_version"),
        version_report.get("active_version"),
    ]

    for version in possible_versions:
        if version:
            return str(version)

    return "UNKNOWN"


def extract_decision(decision_report: dict) -> str:
    """
    Extract the final retraining decision.

    Supports direct and nested decision structures.
    """

    possible_decisions = [
        decision_report.get("final_decision"),
        decision_report.get("decision"),
        decision_report.get("retraining_decision"),
    ]

    for decision in possible_decisions:

        if isinstance(decision, dict):
            nested_decision = (
                decision.get("decision")
                or decision.get("DECISION")
                or decision.get("final_decision")
                or decision.get("FINAL_DECISION")
            )

            if nested_decision:
                return str(nested_decision).upper()

        elif decision:
            return str(decision).upper()

    return "UNKNOWN"


def extract_confidence(decision_report: dict) -> str:
    """
    Extract decision confidence.

    Supports:
        decision_confidence
        confidence
        decision.confidence
    """

    direct_confidences = [
        decision_report.get("decision_confidence"),
        decision_report.get("confidence"),
    ]

    for confidence in direct_confidences:

        if isinstance(confidence, dict):
            nested_confidence = (
                confidence.get("confidence")
                or confidence.get("CONFIDENCE")
                or confidence.get("decision_confidence")
                or confidence.get("DECISION_CONFIDENCE")
            )

            if nested_confidence:
                return str(nested_confidence).upper()

        elif confidence:
            return str(confidence).upper()

    nested_decision = decision_report.get("decision")

    if isinstance(nested_decision, dict):

        nested_confidence = (
            nested_decision.get("confidence")
            or nested_decision.get("CONFIDENCE")
            or nested_decision.get("decision_confidence")
            or nested_decision.get("DECISION_CONFIDENCE")
        )

        if nested_confidence:
            return str(nested_confidence).upper()

    return "UNKNOWN"


# ============================================================
# SCHEDULING LOGIC
# ============================================================

def should_schedule_retraining(
    decision: str,
    trigger_report: dict,
) -> tuple[bool, str]:
    """Determine whether retraining should be scheduled."""

    if decision == "RETRAIN_RECOMMENDED":
        return (
            True,
            "Retraining decision engine explicitly recommends retraining.",
        )

    if decision == "RETRAIN_REVIEW":
        return (
            False,
            "Retraining requires review before scheduling.",
        )

    if decision == "NO_RETRAINING_REQUIRED":
        return (
            False,
            "Current AI signals do not require retraining.",
        )

    trigger_active = bool(
        trigger_report.get("retraining_required", False)
        or trigger_report.get("trigger_retraining", False)
        or trigger_report.get("retraining_triggered", False)
    )

    if trigger_active:
        return (
            True,
            "Existing automated retraining trigger requires retraining.",
        )

    return (
        False,
        "No valid retraining signal was found.",
    )


def calculate_schedule(
    should_schedule: bool,
    cooldown_hours: int = DEFAULT_COOLDOWN_HOURS,
    window_hours: int = DEFAULT_RETRAINING_WINDOW_HOURS,
) -> dict:
    """Create the proposed retraining schedule."""

    now = datetime.now()

    if should_schedule:

        scheduled_start = now + timedelta(hours=cooldown_hours)
        scheduled_end = (
            scheduled_start
            + timedelta(hours=window_hours)
        )

        return {
            "schedule_status": "SCHEDULED",
            "scheduled_start": scheduled_start.isoformat(),
            "scheduled_end": scheduled_end.isoformat(),
            "cooldown_hours": cooldown_hours,
            "retraining_window_hours": window_hours,
        }

    return {
        "schedule_status": "NOT_SCHEDULED",
        "scheduled_start": None,
        "scheduled_end": None,
        "cooldown_hours": cooldown_hours,
        "retraining_window_hours": window_hours,
    }


# ============================================================
# MAIN SCHEDULER
# ============================================================

def run_retraining_scheduler() -> dict:
    """Run the AI retraining scheduling engine."""

    print("=" * 90)
    print("SUPPLYPRESCRIPT - AI RETRAINING SCHEDULER")
    print("=" * 90)

    print()
    print("Loading retraining decision report...")

    decision_report = load_json_file(
        RETRAINING_DECISION_FILE,
        "Retraining decision report",
    )

    print()
    print("Loading existing retraining trigger report...")

    trigger_report = load_json_file(
        RETRAINING_TRIGGER_FILE,
        "Retraining trigger report",
    )

    print()
    print("Loading model version information...")

    version_report = load_json_file(
        MODEL_VERSION_FILE,
        "Model version report",
    )

    decision = extract_decision(decision_report)
    confidence = extract_confidence(decision_report)

    model_version = extract_model_version(
        decision_report,
        version_report,
    )

    schedule_required, schedule_reason = should_schedule_retraining(
        decision,
        trigger_report,
    )

    schedule_details = calculate_schedule(
        should_schedule=schedule_required,
        cooldown_hours=DEFAULT_COOLDOWN_HOURS,
        window_hours=DEFAULT_RETRAINING_WINDOW_HOURS,
    )

    generated_at = datetime.now().isoformat()

    schedule_report = {
        "engine": "AI Retraining Scheduler",
        "generated_at": generated_at,
        "model_version": model_version,
        "retraining_decision": decision,
        "decision_confidence": confidence,
        "schedule_required": schedule_required,
        "schedule_reason": schedule_reason,
        "schedule": schedule_details,
        "operational_scope": {
            "model_artifacts_modified": False,
            "model_retrained": False,
            "scheduler_only": True,
        },
        "next_action": (
            "Execute retraining workflow during the scheduled window."
            if schedule_required
            else "Continue normal AI monitoring."
        ),
    }

    print()
    print("=" * 90)
    print("RETRAINING SCHEDULING RESULT")
    print("=" * 90)

    print()
    print(f"Model Version: {model_version}")
    print(f"Retraining Decision: {decision}")
    print(f"Decision Confidence: {confidence}")
    print(f"Schedule Required: {schedule_required}")

    print()
    print("Scheduling Decision:")

    if schedule_required:
        print("   SCHEDULED")
        print(
            f"   Start: {schedule_details['scheduled_start']}"
        )
        print(
            f"   End:   {schedule_details['scheduled_end']}"
        )
    else:
        print("   NOT_SCHEDULED")

    print()
    print("Reason:")
    print(f"   {schedule_reason}")

    print()
    print("Operational Scope:")
    print("   Recommendation and scheduling only.")
    print("   No model artifacts modified.")
    print("   No model retraining executed.")

    save_json_file(
        OUTPUT_FILE,
        schedule_report,
    )

    print()
    print("=" * 90)
    print("AI RETRAINING SCHEDULER COMPLETED")
    print("=" * 90)

    return schedule_report


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_retraining_scheduler()