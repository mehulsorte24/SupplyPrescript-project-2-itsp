"""
SupplyPrescript - AI Retraining Schedule Health Monitor

Purpose
-------
Monitors the health and operational consistency of the generated
AI retraining schedule and its validation report.

This engine does NOT:
- modify the retraining schedule
- retrain any model
- modify model artifacts
- execute scheduled retraining

It only reads existing reports and produces a health report.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RETRAINING_DIR = BASE_DIR / "ai_engine" / "retraining"

SCHEDULE_FILE = RETRAINING_DIR / "retraining_schedule.json"
VALIDATION_FILE = RETRAINING_DIR / "schedule_validation_report.json"
OUTPUT_FILE = RETRAINING_DIR / "schedule_health_report.json"


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def add_check(
    checks: List[Dict[str, Any]],
    name: str,
    status: str,
    message: str,
) -> None:
    """Add a monitoring check."""

    checks.append(
        {
            "check": name,
            "status": status,
            "message": message,
        }
    )


# ---------------------------------------------------------------------
# SCHEDULE CHECKS
# ---------------------------------------------------------------------

def check_model_version(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check model version."""

    model_version = schedule.get("model_version")

    if model_version:
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
            "FAIL",
            "Model version is missing.",
        )


def check_retraining_decision(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check retraining decision."""

    decision = schedule.get("retraining_decision")

    valid_decisions = {
        "RETRAIN_REQUIRED",
        "RETRAINING_REQUIRED",
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
            f"Invalid retraining decision: {decision}.",
        )


def check_schedule_required_flag(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check schedule_required."""

    schedule_required = schedule.get("schedule_required")

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
            "Schedule required flag must be a boolean.",
        )


def check_schedule_object(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check that the schedule object exists."""

    schedule_config = schedule.get("schedule")

    if isinstance(schedule_config, dict):
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


def check_schedule_status(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check schedule status from the nested schedule object."""

    schedule_config = schedule.get("schedule", {})

    if not isinstance(schedule_config, dict):
        add_check(
            checks,
            "SCHEDULE_STATUS",
            "FAIL",
            "Schedule configuration is not a valid object.",
        )
        return

    schedule_status = schedule_config.get("schedule_status")

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
            f"Invalid or missing schedule status: {schedule_status}.",
        )


def check_decision_schedule_consistency(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check consistency between decision and schedule state."""

    decision = schedule.get("retraining_decision")
    schedule_required = schedule.get("schedule_required")

    schedule_config = schedule.get("schedule", {})

    if not isinstance(schedule_config, dict):
        add_check(
            checks,
            "DECISION_SCHEDULE_CONSISTENCY",
            "FAIL",
            "Schedule configuration is missing.",
        )
        return

    schedule_status = schedule_config.get("schedule_status")

    if decision == "NO_RETRAINING_REQUIRED":

        if (
            schedule_required is False
            and schedule_status == "NOT_SCHEDULED"
        ):
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
                "No-retraining decision conflicts with schedule state.",
            )

    elif decision in {
        "RETRAIN_REQUIRED",
        "RETRAINING_REQUIRED",
    }:

        if (
            schedule_required is True
            and schedule_status == "SCHEDULED"
        ):
            add_check(
                checks,
                "DECISION_SCHEDULE_CONSISTENCY",
                "PASS",
                "Retraining-required decision correctly has a schedule.",
            )
        else:
            add_check(
                checks,
                "DECISION_SCHEDULE_CONSISTENCY",
                "FAIL",
                "Retraining-required decision conflicts with schedule state.",
            )

    else:
        add_check(
            checks,
            "DECISION_SCHEDULE_CONSISTENCY",
            "FAIL",
            "Cannot evaluate decision and schedule consistency.",
        )


# ---------------------------------------------------------------------
# VALIDATION REPORT CHECKS
# ---------------------------------------------------------------------

def check_validation_status(
    validation: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check validation status from the nested validation object."""

    validation_data = validation.get("validation", {})

    if not isinstance(validation_data, dict):
        add_check(
            checks,
            "SCHEDULE_VALIDATION",
            "FAIL",
            "Validation object is missing.",
        )
        return

    validation_status = validation_data.get("validation_status")

    if validation_status == "VALID":
        add_check(
            checks,
            "SCHEDULE_VALIDATION",
            "PASS",
            "Schedule validation report confirms a valid schedule.",
        )

    elif validation_status == "WARNING":
        add_check(
            checks,
            "SCHEDULE_VALIDATION",
            "WARNING",
            "Schedule validation completed with warnings.",
        )

    else:
        add_check(
            checks,
            "SCHEDULE_VALIDATION",
            "FAIL",
            f"Schedule validation status is {validation_status}.",
        )


def check_validation_score(
    validation: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check validation score."""

    validation_data = validation.get("validation", {})

    if not isinstance(validation_data, dict):
        add_check(
            checks,
            "VALIDATION_SCORE",
            "FAIL",
            "Validation object is missing.",
        )
        return

    score = validation_data.get("validation_score")

    if isinstance(score, (int, float)):

        if score >= 90:
            add_check(
                checks,
                "VALIDATION_SCORE",
                "PASS",
                f"Schedule validation score is {score:.1f}%.",
            )

        elif score >= 70:
            add_check(
                checks,
                "VALIDATION_SCORE",
                "WARNING",
                f"Schedule validation score is {score:.1f}%.",
            )

        else:
            add_check(
                checks,
                "VALIDATION_SCORE",
                "FAIL",
                f"Schedule validation score is critically low: {score:.1f}%.",
            )

    else:
        add_check(
            checks,
            "VALIDATION_SCORE",
            "FAIL",
            "Validation score is missing or invalid.",
        )


# ---------------------------------------------------------------------
# OPERATIONAL SAFETY CHECKS
# ---------------------------------------------------------------------

def check_operational_scope(
    schedule: Dict[str, Any],
    validation: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Verify that the scheduler and validator remain passive."""

    schedule_scope = schedule.get("operational_scope", {})
    validation_scope = validation.get("operational_scope", {})

    if not isinstance(schedule_scope, dict):
        add_check(
            checks,
            "SCHEDULER_OPERATIONAL_SCOPE",
            "FAIL",
            "Scheduler operational scope is missing.",
        )
        return

    if not isinstance(validation_scope, dict):
        add_check(
            checks,
            "VALIDATOR_OPERATIONAL_SCOPE",
            "FAIL",
            "Validator operational scope is missing.",
        )
        return

    scheduler_safe = (
        schedule_scope.get("model_artifacts_modified") is False
        and schedule_scope.get("model_retrained") is False
        and schedule_scope.get("scheduler_only") is True
    )

    validator_safe = (
        validation_scope.get("schedule_modified") is False
        and validation_scope.get("model_artifacts_modified") is False
        and validation_scope.get("model_retrained") is False
        and validation_scope.get("validator_only") is True
    )

    if scheduler_safe:
        add_check(
            checks,
            "SCHEDULER_OPERATIONAL_SCOPE",
            "PASS",
            "Scheduler remains within passive scheduling scope.",
        )
    else:
        add_check(
            checks,
            "SCHEDULER_OPERATIONAL_SCOPE",
            "FAIL",
            "Scheduler operational scope contains an unsafe state.",
        )

    if validator_safe:
        add_check(
            checks,
            "VALIDATOR_OPERATIONAL_SCOPE",
            "PASS",
            "Validator remains within validation-only scope.",
        )
    else:
        add_check(
            checks,
            "VALIDATOR_OPERATIONAL_SCOPE",
            "FAIL",
            "Validator operational scope contains an unsafe state.",
        )


# ---------------------------------------------------------------------
# REPORT CONSISTENCY
# ---------------------------------------------------------------------

def check_report_consistency(
    schedule: Dict[str, Any],
    validation: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Compare common values between the two reports."""

    schedule_version = schedule.get("model_version")
    validation_version = validation.get("model_version")

    schedule_decision = schedule.get("retraining_decision")
    validation_decision = validation.get("retraining_decision")

    version_match = (
        schedule_version
        and validation_version
        and schedule_version == validation_version
    )

    decision_match = (
        schedule_decision
        and validation_decision
        and schedule_decision == validation_decision
    )

    if version_match:
        add_check(
            checks,
            "REPORT_VERSION_CONSISTENCY",
            "PASS",
            f"Schedule and validation reports use model version {schedule_version}.",
        )
    else:
        add_check(
            checks,
            "REPORT_VERSION_CONSISTENCY",
            "FAIL",
            "Schedule and validation reports contain different model versions.",
        )

    if decision_match:
        add_check(
            checks,
            "REPORT_DECISION_CONSISTENCY",
            "PASS",
            f"Both reports use decision {schedule_decision}.",
        )
    else:
        add_check(
            checks,
            "REPORT_DECISION_CONSISTENCY",
            "FAIL",
            "Schedule and validation reports contain different retraining decisions.",
        )


# ---------------------------------------------------------------------
# HEALTH CALCULATION
# ---------------------------------------------------------------------

def calculate_health(
    checks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate overall health."""

    total_checks = len(checks)

    passed = sum(
        1
        for check in checks
        if check["status"] == "PASS"
    )

    warnings = sum(
        1
        for check in checks
        if check["status"] == "WARNING"
    )

    failed = sum(
        1
        for check in checks
        if check["status"] == "FAIL"
    )

    if total_checks == 0:
        health_score = 0.0
    else:
        health_score = round(
            (
                (passed + (warnings * 0.5))
                / total_checks
            )
            * 100,
            2,
        )

    if failed > 0:
        health_status = "UNHEALTHY"
    elif warnings > 0:
        health_status = "HEALTHY_WITH_WARNINGS"
    else:
        health_status = "HEALTHY"

    return {
        "health_status": health_status,
        "health_score": health_score,
        "total_checks": total_checks,
        "passed_checks": passed,
        "warning_checks": warnings,
        "failed_checks": failed,
    }


# ---------------------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------------------

def monitor_schedule_health() -> Dict[str, Any]:
    """Run the complete schedule health monitoring process."""

    print("=" * 100)
    print("SUPPLYPRESCRIPT - AI RETRAINING SCHEDULE HEALTH MONITOR")
    print("=" * 100)
    print()

    # ---------------------------------------------------------------
    # LOAD SCHEDULE
    # ---------------------------------------------------------------

    print("Loading retraining schedule...")

    if not SCHEDULE_FILE.exists():
        raise FileNotFoundError(
            f"Retraining schedule not found:\n{SCHEDULE_FILE}"
        )

    schedule = load_json(SCHEDULE_FILE)

    print("   ✓ Retraining schedule loaded.")
    print()

    # ---------------------------------------------------------------
    # LOAD VALIDATION REPORT
    # ---------------------------------------------------------------

    print("Loading schedule validation report...")

    if not VALIDATION_FILE.exists():
        raise FileNotFoundError(
            f"Schedule validation report not found:\n{VALIDATION_FILE}"
        )

    validation = load_json(VALIDATION_FILE)

    print("   ✓ Schedule validation report loaded.")
    print()

    # ---------------------------------------------------------------
    # RUN CHECKS
    # ---------------------------------------------------------------

    checks: List[Dict[str, Any]] = []

    check_model_version(
        schedule,
        checks,
    )

    check_retraining_decision(
        schedule,
        checks,
    )

    check_schedule_required_flag(
        schedule,
        checks,
    )

    check_schedule_object(
        schedule,
        checks,
    )

    check_schedule_status(
        schedule,
        checks,
    )

    check_decision_schedule_consistency(
        schedule,
        checks,
    )

    check_validation_status(
        validation,
        checks,
    )

    check_validation_score(
        validation,
        checks,
    )

    check_operational_scope(
        schedule,
        validation,
        checks,
    )

    check_report_consistency(
        schedule,
        validation,
        checks,
    )

    # ---------------------------------------------------------------
    # CALCULATE HEALTH
    # ---------------------------------------------------------------

    health = calculate_health(checks)

    model_version = schedule.get(
        "model_version",
        "UNKNOWN",
    )

    retraining_decision = schedule.get(
        "retraining_decision",
        "UNKNOWN",
    )

    schedule_config = schedule.get(
        "schedule",
        {},
    )

    if isinstance(schedule_config, dict):
        schedule_status = schedule_config.get(
            "schedule_status",
            "UNKNOWN",
        )
    else:
        schedule_status = "UNKNOWN"

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    # ---------------------------------------------------------------
    # BUILD REPORT
    # ---------------------------------------------------------------

    report = {
        "engine": "AI Retraining Schedule Health Monitor",
        "generated_at": generated_at,
        "model_version": model_version,
        "retraining_decision": retraining_decision,
        "schedule_status": schedule_status,
        "health": health,
        "checks": checks,
        "operational_scope": {
            "schedule_modified": False,
            "model_artifacts_modified": False,
            "model_retrained": False,
            "monitoring_only": True,
        },
        "next_action": (
            "Continue normal AI monitoring."
            if health["health_status"] == "HEALTHY"
            else "Review schedule health issues before proceeding."
        ),
    }

    # ---------------------------------------------------------------
    # SAVE REPORT
    # ---------------------------------------------------------------

    RETRAINING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
        )

    # ---------------------------------------------------------------
    # CONSOLE OUTPUT
    # ---------------------------------------------------------------

    print("=" * 100)
    print("SCHEDULE HEALTH RESULT")
    print("=" * 100)
    print()

    print(f"Model Version: {model_version}")
    print(f"Retraining Decision: {retraining_decision}")
    print(f"Schedule Status: {schedule_status}")
    print(
        f"Health Status: "
        f"{health['health_status']}"
    )
    print(
        f"Health Score: "
        f"{health['health_score']:.2f}%"
    )
    print(
        f"Passed Checks: "
        f"{health['passed_checks']}"
    )
    print(
        f"Warnings: "
        f"{health['warning_checks']}"
    )
    print(
        f"Failed Checks: "
        f"{health['failed_checks']}"
    )
    print()

    print("Health Checks:")

    for check in checks:
        print(
            f"   {check['status']:<8} - "
            f"{check['check']}: "
            f"{check['message']}"
        )

    print()
    print("Operational Scope:")
    print("   Schedule health monitoring only.")
    print("   No schedule modified.")
    print("   No model artifacts modified.")
    print("   No model retraining executed.")
    print()

    print("✓ Schedule health report saved:")
    print(f"  {OUTPUT_FILE}")

    return report


# ---------------------------------------------------------------------
# SCRIPT ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    monitor_schedule_health()