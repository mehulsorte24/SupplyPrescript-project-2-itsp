from pathlib import Path
import json
from datetime import datetime


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCHEDULE_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_schedule.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "schedule_validation_report.json"
)


# ============================================================
# VALIDATION CONFIGURATION
# ============================================================

MIN_COOLDOWN_HOURS = 1
MAX_COOLDOWN_HOURS = 168

MIN_RETRAINING_WINDOW_HOURS = 1
MAX_RETRAINING_WINDOW_HOURS = 24


# ============================================================
# FILE HELPERS
# ============================================================

def load_json_file(file_path: Path, label: str) -> dict:
    """Load a JSON file safely."""

    if not file_path.exists():
        print(f"   ✗ {label} not found:")
        print(f"     {file_path}")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        print(f"   ✓ {label} found.")
        return data

    except json.JSONDecodeError as error:
        print(f"   ✗ Failed to parse {label}:")
        print(f"     {error}")
        return {}

    except OSError as error:
        print(f"   ✗ Failed to read {label}:")
        print(f"     {error}")
        return {}


def save_json_file(file_path: Path, data: dict) -> None:
    """Save validation report as formatted JSON."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print()
    print("✓ Schedule validation report saved:")
    print(f"  {file_path}")


# ============================================================
# VALIDATION HELPERS
# ============================================================

def add_check(
    checks: list,
    name: str,
    result: str,
    message: str,
) -> None:
    """Add a validation check to the report."""

    checks.append(
        {
            "check": name,
            "result": result,
            "message": message,
        }
    )


def parse_datetime(value: str):
    """Parse an ISO formatted datetime."""

    try:
        return datetime.fromisoformat(value)

    except (TypeError, ValueError):
        return None


# ============================================================
# SCHEDULE VALIDATION
# ============================================================

def validate_schedule(schedule_report: dict) -> dict:
    """
    Validate the AI retraining schedule.

    Returns a structured validation report.
    """

    checks = []
    errors = []
    warnings = []

    if not schedule_report:
        add_check(
            checks,
            "SCHEDULE_FILE",
            "FAIL",
            "Retraining schedule report could not be loaded.",
        )

        errors.append(
            "Retraining schedule report is unavailable."
        )

        return {
            "validation_status": "INVALID",
            "validation_score": 0,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
        }

    # --------------------------------------------------------
    # Model Version Check
    # --------------------------------------------------------

    model_version = schedule_report.get("model_version")

    if model_version and str(model_version).upper() != "UNKNOWN":

        add_check(
            checks,
            "MODEL_VERSION",
            "PASS",
            f"Model version {model_version} is available.",
        )

    else:

        add_check(
            checks,
            "MODEL_VERSION",
            "WARNING",
            "Model version is unknown.",
        )

        warnings.append(
            "Model version could not be fully identified."
        )

    # --------------------------------------------------------
    # Retraining Decision Check
    # --------------------------------------------------------

    decision = str(
        schedule_report.get(
            "retraining_decision",
            "UNKNOWN",
        )
    ).upper()

    valid_decisions = {
        "RETRAIN_RECOMMENDED",
        "RETRAIN_REVIEW",
        "NO_RETRAINING_REQUIRED",
    }

    if decision in valid_decisions:

        add_check(
            checks,
            "RETRAINING_DECISION",
            "PASS",
            f"Valid retraining decision: {decision}.",
        )

    else:

        add_check(
            checks,
            "RETRAINING_DECISION",
            "FAIL",
            f"Unknown retraining decision: {decision}.",
        )

        errors.append(
            "Retraining decision is missing or invalid."
        )

    # --------------------------------------------------------
    # Schedule Required Check
    # --------------------------------------------------------

    schedule_required = schedule_report.get(
        "schedule_required"
    )

    if isinstance(schedule_required, bool):

        add_check(
            checks,
            "SCHEDULE_REQUIRED_FLAG",
            "PASS",
            f"Schedule required flag is valid: {schedule_required}.",
        )

    else:

        add_check(
            checks,
            "SCHEDULE_REQUIRED_FLAG",
            "FAIL",
            "Schedule required flag must be boolean.",
        )

        errors.append(
            "Schedule required flag is invalid."
        )

    # --------------------------------------------------------
    # Schedule Object Check
    # --------------------------------------------------------

    schedule = schedule_report.get("schedule")

    if isinstance(schedule, dict):

        add_check(
            checks,
            "SCHEDULE_OBJECT",
            "PASS",
            "Schedule configuration object is present.",
        )

    else:

        add_check(
            checks,
            "SCHEDULE_OBJECT",
            "FAIL",
            "Schedule configuration object is missing.",
        )

        errors.append(
            "Schedule configuration is missing."
        )

        schedule = {}

    # --------------------------------------------------------
    # Schedule Status Check
    # --------------------------------------------------------

    schedule_status = str(
        schedule.get(
            "schedule_status",
            "UNKNOWN",
        )
    ).upper()

    valid_statuses = {
        "SCHEDULED",
        "NOT_SCHEDULED",
    }

    if schedule_status in valid_statuses:

        add_check(
            checks,
            "SCHEDULE_STATUS",
            "PASS",
            f"Valid schedule status: {schedule_status}.",
        )

    else:

        add_check(
            checks,
            "SCHEDULE_STATUS",
            "FAIL",
            f"Unknown schedule status: {schedule_status}.",
        )

        errors.append(
            "Schedule status is invalid."
        )

    # --------------------------------------------------------
    # Decision / Schedule Consistency
    # --------------------------------------------------------

    if decision == "NO_RETRAINING_REQUIRED":

        if schedule_required is False:

            add_check(
                checks,
                "DECISION_SCHEDULE_CONSISTENCY",
                "PASS",
                "No-retraining decision correctly has no schedule.",
            )

        else:

            add_check(
                checks,
                "DECISION_SCHEDULE_CONSISTENCY",
                "FAIL",
                "No-retraining decision cannot require a schedule.",
            )

            errors.append(
                "Schedule is inconsistent with the retraining decision."
            )

    elif decision == "RETRAIN_RECOMMENDED":

        if schedule_required is True:

            add_check(
                checks,
                "DECISION_SCHEDULE_CONSISTENCY",
                "PASS",
                "Retraining recommendation correctly has a schedule.",
            )

        else:

            add_check(
                checks,
                "DECISION_SCHEDULE_CONSISTENCY",
                "WARNING",
                "Retraining is recommended but no schedule is active.",
            )

            warnings.append(
                "Retraining is recommended but scheduling is not active."
            )

    elif decision == "RETRAIN_REVIEW":

        add_check(
            checks,
            "DECISION_SCHEDULE_CONSISTENCY",
            "PASS",
            "Retraining review decision does not automatically schedule retraining.",
        )

    # --------------------------------------------------------
    # Cooldown Check
    # --------------------------------------------------------

    cooldown_hours = schedule.get("cooldown_hours")

    if isinstance(cooldown_hours, (int, float)):

        if MIN_COOLDOWN_HOURS <= cooldown_hours <= MAX_COOLDOWN_HOURS:

            add_check(
                checks,
                "COOLDOWN_PERIOD",
                "PASS",
                f"Cooldown period is valid: {cooldown_hours} hours.",
            )

        else:

            add_check(
                checks,
                "COOLDOWN_PERIOD",
                "FAIL",
                (
                    f"Cooldown period {cooldown_hours} hours "
                    f"is outside the allowed range."
                ),
            )

            errors.append(
                "Cooldown period is outside the allowed range."
            )

    else:

        add_check(
            checks,
            "COOLDOWN_PERIOD",
            "FAIL",
            "Cooldown period is missing or invalid.",
        )

        errors.append(
            "Cooldown period is invalid."
        )

    # --------------------------------------------------------
    # Retraining Window Check
    # --------------------------------------------------------

    window_hours = schedule.get(
        "retraining_window_hours"
    )

    if isinstance(window_hours, (int, float)):

        if (
            MIN_RETRAINING_WINDOW_HOURS
            <= window_hours
            <= MAX_RETRAINING_WINDOW_HOURS
        ):

            add_check(
                checks,
                "RETRAINING_WINDOW",
                "PASS",
                f"Retraining window is valid: {window_hours} hours.",
            )

        else:

            add_check(
                checks,
                "RETRAINING_WINDOW",
                "FAIL",
                (
                    f"Retraining window {window_hours} hours "
                    f"is outside the allowed range."
                ),
            )

            errors.append(
                "Retraining window is outside the allowed range."
            )

    else:

        add_check(
            checks,
            "RETRAINING_WINDOW",
            "FAIL",
            "Retraining window is missing or invalid.",
        )

        errors.append(
            "Retraining window is invalid."
        )

    # --------------------------------------------------------
    # Scheduled Time Validation
    # --------------------------------------------------------

    scheduled_start = schedule.get(
        "scheduled_start"
    )

    scheduled_end = schedule.get(
        "scheduled_end"
    )

    if schedule_status == "SCHEDULED":

        if not scheduled_start or not scheduled_end:

            add_check(
                checks,
                "SCHEDULE_TIMESTAMPS",
                "FAIL",
                "Scheduled start and end timestamps are required.",
            )

            errors.append(
                "Scheduled timestamps are missing."
            )

        else:

            start_time = parse_datetime(
                scheduled_start
            )

            end_time = parse_datetime(
                scheduled_end
            )

            if start_time is None or end_time is None:

                add_check(
                    checks,
                    "SCHEDULE_TIMESTAMPS",
                    "FAIL",
                    "Scheduled timestamps are not valid ISO datetime values.",
                )

                errors.append(
                    "Scheduled timestamps are invalid."
                )

            elif start_time >= end_time:

                add_check(
                    checks,
                    "SCHEDULE_TIMESTAMPS",
                    "FAIL",
                    "Scheduled start time must be before the end time.",
                )

                errors.append(
                    "Scheduled start time is not before the end time."
                )

            else:

                add_check(
                    checks,
                    "SCHEDULE_TIMESTAMPS",
                    "PASS",
                    "Scheduled start and end timestamps are valid.",
                )

    else:

        add_check(
            checks,
            "SCHEDULE_TIMESTAMPS",
            "PASS",
            "No timestamps are required because retraining is not scheduled.",
        )

    # --------------------------------------------------------
    # Operational Scope Check
    # --------------------------------------------------------

    operational_scope = schedule_report.get(
        "operational_scope"
    )

    if isinstance(operational_scope, dict):

        artifacts_modified = operational_scope.get(
            "model_artifacts_modified"
        )

        model_retrained = operational_scope.get(
            "model_retrained"
        )

        if (
            artifacts_modified is False
            and model_retrained is False
        ):

            add_check(
                checks,
                "OPERATIONAL_SCOPE",
                "PASS",
                "Scheduler does not modify or retrain model artifacts.",
            )

        else:

            add_check(
                checks,
                "OPERATIONAL_SCOPE",
                "WARNING",
                "Scheduler report indicates possible model modification.",
            )

            warnings.append(
                "Scheduler scope should remain recommendation-only."
            )

    else:

        add_check(
            checks,
            "OPERATIONAL_SCOPE",
            "WARNING",
            "Operational scope information is unavailable.",
        )

        warnings.append(
            "Operational scope could not be verified."
        )

    # --------------------------------------------------------
    # Final Score
    # --------------------------------------------------------

    total_checks = len(checks)

    passed_checks = sum(
        1
        for check in checks
        if check["result"] == "PASS"
    )

    failed_checks = sum(
        1
        for check in checks
        if check["result"] == "FAIL"
    )

    if total_checks > 0:

        validation_score = round(
            (passed_checks / total_checks) * 100,
            2,
        )

    else:

        validation_score = 0

    if failed_checks > 0:

        validation_status = "INVALID"

    elif warnings:

        validation_status = "VALID_WITH_WARNINGS"

    else:

        validation_status = "VALID"

    return {
        "validation_status": validation_status,
        "validation_score": validation_score,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "warning_count": len(warnings),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# MAIN VALIDATOR
# ============================================================

def run_schedule_validator() -> dict:
    """Run the AI retraining schedule validator."""

    print("=" * 90)
    print("SUPPLYPRESCRIPT - AI RETRAINING SCHEDULE VALIDATOR")
    print("=" * 90)

    print()
    print("Loading retraining schedule...")

    schedule_report = load_json_file(
        SCHEDULE_FILE,
        "Retraining schedule report",
    )

    validation_result = validate_schedule(
        schedule_report
    )

    final_report = {
        "engine": "AI Retraining Schedule Validator",
        "generated_at": datetime.now().isoformat(),
        "model_version": schedule_report.get(
            "model_version",
            "UNKNOWN",
        ),
        "retraining_decision": schedule_report.get(
            "retraining_decision",
            "UNKNOWN",
        ),
        "validation": validation_result,
        "operational_scope": {
            "schedule_modified": False,
            "model_artifacts_modified": False,
            "model_retrained": False,
            "validator_only": True,
        },
        "next_action": (
            "Retraining schedule is valid and may proceed to the retraining workflow."
            if validation_result["validation_status"] == "VALID"
            else (
                "Review warnings before proceeding."
                if validation_result["validation_status"]
                == "VALID_WITH_WARNINGS"
                else
                "Do not proceed until schedule validation failures are resolved."
            )
        ),
    }

    print()
    print("=" * 90)
    print("SCHEDULE VALIDATION RESULT")
    print("=" * 90)

    print()
    print(
        f"Model Version: "
        f"{final_report['model_version']}"
    )

    print(
        f"Retraining Decision: "
        f"{final_report['retraining_decision']}"
    )

    print(
        f"Validation Status: "
        f"{validation_result['validation_status']}"
    )

    print(
        f"Validation Score: "
        f"{validation_result['validation_score']}%"
    )

    print(
        f"Passed Checks: "
        f"{validation_result['passed_checks']}"
    )

    print(
        f"Failed Checks: "
        f"{validation_result['failed_checks']}"
    )

    print(
        f"Warnings: "
        f"{validation_result['warning_count']}"
    )

    print()
    print("Validation Checks:")

    for check in validation_result["checks"]:

        print(
            f"   {check['result']:<8} "
            f"- {check['check']}: "
            f"{check['message']}"
        )

    if validation_result["errors"]:

        print()
        print("Errors:")

        for error in validation_result["errors"]:
            print(f"   ✗ {error}")

    if validation_result["warnings"]:

        print()
        print("Warnings:")

        for warning in validation_result["warnings"]:
            print(f"   ! {warning}")

    print()
    print("Operational Scope:")
    print("   Schedule validation only.")
    print("   No schedule modified.")
    print("   No model artifacts modified.")
    print("   No model retraining executed.")

    save_json_file(
        OUTPUT_FILE,
        final_report,
    )

    print()
    print("=" * 90)
    print("AI RETRAINING SCHEDULE VALIDATOR COMPLETED")
    print("=" * 90)

    return final_report


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_schedule_validator()