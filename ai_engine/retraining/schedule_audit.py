"""
SupplyPrescript - AI Retraining Schedule Audit Engine

Purpose
-------
Creates an auditable record of the AI retraining lifecycle:

    Retraining Decision
            ↓
    Retraining Schedule
            ↓
    Schedule Validation
            ↓
    Schedule Health
            ↓
    Audit Record

This engine is read-only.

It does NOT:
- modify schedules
- modify model artifacts
- retrain models
- execute retraining
- change retraining decisions

It creates an audit trail for governance and observability.
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

DECISION_FILE = RETRAINING_DIR / "retraining_decision_report.json"
SCHEDULE_FILE = RETRAINING_DIR / "retraining_schedule.json"
VALIDATION_FILE = RETRAINING_DIR / "schedule_validation_report.json"
HEALTH_FILE = RETRAINING_DIR / "schedule_health_report.json"

OUTPUT_FILE = RETRAINING_DIR / "retraining_schedule_audit.json"


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON document."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def file_status(file_path: Path) -> Dict[str, Any]:
    """Return basic availability information for a report."""

    return {
        "file": file_path.name,
        "available": file_path.exists(),
    }


def add_audit_check(
    checks: List[Dict[str, Any]],
    name: str,
    status: str,
    message: str,
) -> None:
    """Add an audit check."""

    checks.append(
        {
            "check": name,
            "status": status,
            "message": message,
        }
    )


# ---------------------------------------------------------------------
# AUDIT CHECKS
# ---------------------------------------------------------------------

def check_decision_consistency(
    decision: Dict[str, Any],
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Compare retraining decision across decision and schedule reports."""

    decision_data = decision.get("decision", {})

    decision_value = decision_data.get(
        "decision",
        decision.get("retraining_decision"),
    )

    schedule_decision = schedule.get(
        "retraining_decision"
    )

    if (
        decision_value
        and schedule_decision
        and decision_value == schedule_decision
    ):
        add_audit_check(
            checks,
            "DECISION_CONSISTENCY",
            "PASS",
            (
                "Retraining decision is consistent across "
                f"decision and schedule reports: {decision_value}."
            ),
        )
    else:
        add_audit_check(
            checks,
            "DECISION_CONSISTENCY",
            "FAIL",
            (
                "Retraining decision differs between "
                "decision and schedule reports."
            ),
        )


def check_model_version_consistency(
    decision: Dict[str, Any],
    schedule: Dict[str, Any],
    validation: Dict[str, Any],
    health: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check model version consistency across all available reports."""

    versions = {
        "decision": decision.get("model_version"),
        "schedule": schedule.get("model_version"),
        "validation": validation.get("model_version"),
        "health": health.get("model_version"),
    }

    available_versions = [
        version
        for version in versions.values()
        if version
    ]

    if not available_versions:
        add_audit_check(
            checks,
            "MODEL_VERSION_CONSISTENCY",
            "FAIL",
            "No model version was found in the audit sources.",
        )
        return

    if len(set(available_versions)) == 1:
        model_version = available_versions[0]

        add_audit_check(
            checks,
            "MODEL_VERSION_CONSISTENCY",
            "PASS",
            (
                "All available reports use model version "
                f"{model_version}."
            ),
        )
    else:
        add_audit_check(
            checks,
            "MODEL_VERSION_CONSISTENCY",
            "FAIL",
            (
                "Different model versions were found across "
                f"reports: {versions}."
            ),
        )


def check_validation_health(
    validation: Dict[str, Any],
    health: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Compare validation and health results."""

    validation_data = validation.get(
        "validation",
        {},
    )

    validation_status = validation_data.get(
        "validation_status"
    )

    health_data = health.get(
        "health",
        {},
    )

    health_status = health_data.get(
        "health_status"
    )

    if (
        validation_status == "VALID"
        and health_status == "HEALTHY"
    ):
        add_audit_check(
            checks,
            "VALIDATION_HEALTH_CONSISTENCY",
            "PASS",
            (
                "Schedule validation is VALID and "
                "schedule health is HEALTHY."
            ),
        )

    elif (
        validation_status == "WARNING"
        or health_status == "HEALTHY_WITH_WARNINGS"
    ):
        add_audit_check(
            checks,
            "VALIDATION_HEALTH_CONSISTENCY",
            "WARNING",
            (
                "Validation or health monitoring reported "
                "warnings."
            ),
        )

    else:
        add_audit_check(
            checks,
            "VALIDATION_HEALTH_CONSISTENCY",
            "FAIL",
            (
                "Validation and health states indicate "
                "an unhealthy schedule."
            ),
        )


def check_schedule_state(
    schedule: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Check schedule state against the retraining decision."""

    decision = schedule.get(
        "retraining_decision"
    )

    schedule_required = schedule.get(
        "schedule_required"
    )

    schedule_data = schedule.get(
        "schedule",
        {},
    )

    schedule_status = schedule_data.get(
        "schedule_status"
    )

    if decision == "NO_RETRAINING_REQUIRED":

        if (
            schedule_required is False
            and schedule_status == "NOT_SCHEDULED"
        ):
            add_audit_check(
                checks,
                "SCHEDULE_STATE",
                "PASS",
                (
                    "No retraining is required and the "
                    "schedule is correctly NOT_SCHEDULED."
                ),
            )
        else:
            add_audit_check(
                checks,
                "SCHEDULE_STATE",
                "FAIL",
                (
                    "No-retraining decision conflicts "
                    "with schedule state."
                ),
            )

    elif decision in {
        "RETRAIN_REQUIRED",
        "RETRAINING_REQUIRED",
    }:

        if (
            schedule_required is True
            and schedule_status == "SCHEDULED"
        ):
            add_audit_check(
                checks,
                "SCHEDULE_STATE",
                "PASS",
                (
                    "Retraining is required and the "
                    "schedule is correctly SCHEDULED."
                ),
            )
        else:
            add_audit_check(
                checks,
                "SCHEDULE_STATE",
                "FAIL",
                (
                    "Retraining-required decision conflicts "
                    "with schedule state."
                ),
            )

    else:
        add_audit_check(
            checks,
            "SCHEDULE_STATE",
            "FAIL",
            "Unable to validate schedule state.",
        )


def check_operational_safety(
    schedule: Dict[str, Any],
    validation: Dict[str, Any],
    health: Dict[str, Any],
    checks: List[Dict[str, Any]],
) -> None:
    """Verify that the audit workflow remains read-only."""

    schedule_scope = schedule.get(
        "operational_scope",
        {},
    )

    validation_scope = validation.get(
        "operational_scope",
        {},
    )

    health_scope = health.get(
        "operational_scope",
        {},
    )

    schedule_safe = (
        isinstance(schedule_scope, dict)
        and schedule_scope.get(
            "model_artifacts_modified"
        ) is False
        and schedule_scope.get(
            "model_retrained"
        ) is False
        and schedule_scope.get(
            "scheduler_only"
        ) is True
    )

    validation_safe = (
        isinstance(validation_scope, dict)
        and validation_scope.get(
            "schedule_modified"
        ) is False
        and validation_scope.get(
            "model_artifacts_modified"
        ) is False
        and validation_scope.get(
            "model_retrained"
        ) is False
        and validation_scope.get(
            "validator_only"
        ) is True
    )

    health_safe = (
        isinstance(health_scope, dict)
        and health_scope.get(
            "schedule_modified"
        ) is False
        and health_scope.get(
            "model_artifacts_modified"
        ) is False
        and health_scope.get(
            "model_retrained"
        ) is False
        and health_scope.get(
            "monitoring_only"
        ) is True
    )

    if (
        schedule_safe
        and validation_safe
        and health_safe
    ):
        add_audit_check(
            checks,
            "OPERATIONAL_SAFETY",
            "PASS",
            (
                "Scheduler, validator, and health monitor "
                "remain within read-only operational scope."
            ),
        )
    else:
        add_audit_check(
            checks,
            "OPERATIONAL_SAFETY",
            "FAIL",
            (
                "One or more upstream components contain "
                "an unsafe operational state."
            ),
        )


def check_required_reports(
    checks: List[Dict[str, Any]],
) -> None:
    """Check that all required audit inputs are available."""

    required_files = [
        DECISION_FILE,
        SCHEDULE_FILE,
        VALIDATION_FILE,
        HEALTH_FILE,
    ]

    missing_files = [
        file_path.name
        for file_path in required_files
        if not file_path.exists()
    ]

    if not missing_files:
        add_audit_check(
            checks,
            "REQUIRED_REPORTS",
            "PASS",
            "All required AI retraining reports are available.",
        )
    else:
        add_audit_check(
            checks,
            "REQUIRED_REPORTS",
            "FAIL",
            (
                "Missing required reports: "
                + ", ".join(missing_files)
            ),
        )


# ---------------------------------------------------------------------
# AUDIT SCORE
# ---------------------------------------------------------------------

def calculate_audit_score(
    checks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate audit score."""

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
        score = 0.0
    else:
        score = round(
            (
                (passed + (warnings * 0.5))
                / total_checks
            )
            * 100,
            2,
        )

    if failed > 0:
        audit_status = "AUDIT_FAILED"
    elif warnings > 0:
        audit_status = "AUDIT_PASSED_WITH_WARNINGS"
    else:
        audit_status = "AUDIT_PASSED"

    return {
        "audit_status": audit_status,
        "audit_score": score,
        "total_checks": total_checks,
        "passed_checks": passed,
        "warning_checks": warnings,
        "failed_checks": failed,
    }


# ---------------------------------------------------------------------
# MAIN AUDIT ENGINE
# ---------------------------------------------------------------------

def run_schedule_audit() -> Dict[str, Any]:
    """Run the complete retraining schedule audit."""

    print("=" * 100)
    print("SUPPLYPRESCRIPT - AI RETRAINING SCHEDULE AUDIT ENGINE")
    print("=" * 100)
    print()

    print("Checking required audit reports...")
    check_files = [
        DECISION_FILE,
        SCHEDULE_FILE,
        VALIDATION_FILE,
        HEALTH_FILE,
    ]

    for file_path in check_files:
        status = file_status(file_path)

        if status["available"]:
            print(
                f"   ✓ {status['file']} available."
            )
        else:
            print(
                f"   ✗ {status['file']} missing."
            )

    print()

    check_required_reports([])

    missing_required = [
        file_path.name
        for file_path in check_files
        if not file_path.exists()
    ]

    if missing_required:
        raise FileNotFoundError(
            "Required audit reports are missing: "
            + ", ".join(missing_required)
        )

    # ---------------------------------------------------------------
    # LOAD REPORTS
    # ---------------------------------------------------------------

    decision = load_json(
        DECISION_FILE
    )

    schedule = load_json(
        SCHEDULE_FILE
    )

    validation = load_json(
        VALIDATION_FILE
    )

    health = load_json(
        HEALTH_FILE
    )

    # ---------------------------------------------------------------
    # RUN AUDIT CHECKS
    # ---------------------------------------------------------------

    checks: List[Dict[str, Any]] = []

    check_required_reports(
        checks
    )

    check_decision_consistency(
        decision,
        schedule,
        checks,
    )

    check_model_version_consistency(
        decision,
        schedule,
        validation,
        health,
        checks,
    )

    check_validation_health(
        validation,
        health,
        checks,
    )

    check_schedule_state(
        schedule,
        checks,
    )

    check_operational_safety(
        schedule,
        validation,
        health,
        checks,
    )

    # ---------------------------------------------------------------
    # CALCULATE AUDIT RESULT
    # ---------------------------------------------------------------

    audit_result = calculate_audit_score(
        checks
    )

    model_version = schedule.get(
        "model_version",
        "UNKNOWN",
    )

    retraining_decision = schedule.get(
        "retraining_decision",
        "UNKNOWN",
    )

    schedule_data = schedule.get(
        "schedule",
        {},
    )

    if isinstance(schedule_data, dict):
        schedule_status = schedule_data.get(
            "schedule_status",
            "UNKNOWN",
        )
    else:
        schedule_status = "UNKNOWN"

    validation_data = validation.get(
        "validation",
        {},
    )

    validation_status = validation_data.get(
        "validation_status",
        "UNKNOWN",
    )

    health_data = health.get(
        "health",
        {},
    )

    health_status = health_data.get(
        "health_status",
        "UNKNOWN",
    )

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    # ---------------------------------------------------------------
    # BUILD AUDIT REPORT
    # ---------------------------------------------------------------

    audit_report = {
        "engine": "AI Retraining Schedule Audit Engine",
        "generated_at": generated_at,
        "model_version": model_version,
        "lifecycle": {
            "retraining_decision": retraining_decision,
            "schedule_status": schedule_status,
            "validation_status": validation_status,
            "health_status": health_status,
        },
        "audit": audit_result,
        "checks": checks,
        "source_reports": {
            "retraining_decision_report": DECISION_FILE.name,
            "retraining_schedule": SCHEDULE_FILE.name,
            "schedule_validation_report": VALIDATION_FILE.name,
            "schedule_health_report": HEALTH_FILE.name,
        },
        "governance": {
            "audit_only": True,
            "schedule_modified": False,
            "model_artifacts_modified": False,
            "model_retrained": False,
            "decision_modified": False,
        },
        "next_action": (
            "Retraining schedule lifecycle audit passed. "
            "Continue normal AI monitoring."
            if audit_result["audit_status"] == "AUDIT_PASSED"
            else "Review audit findings before proceeding."
        ),
    }

    # ---------------------------------------------------------------
    # SAVE AUDIT REPORT
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
            audit_report,
            file,
            indent=4,
        )

    # ---------------------------------------------------------------
    # CONSOLE OUTPUT
    # ---------------------------------------------------------------

    print("=" * 100)
    print("RETRAINING SCHEDULE AUDIT RESULT")
    print("=" * 100)
    print()

    print(
        f"Model Version: {model_version}"
    )

    print(
        f"Retraining Decision: "
        f"{retraining_decision}"
    )

    print(
        f"Schedule Status: "
        f"{schedule_status}"
    )

    print(
        f"Validation Status: "
        f"{validation_status}"
    )

    print(
        f"Health Status: "
        f"{health_status}"
    )

    print(
        f"Audit Status: "
        f"{audit_result['audit_status']}"
    )

    print(
        f"Audit Score: "
        f"{audit_result['audit_score']:.2f}%"
    )

    print(
        f"Passed Checks: "
        f"{audit_result['passed_checks']}"
    )

    print(
        f"Warnings: "
        f"{audit_result['warning_checks']}"
    )

    print(
        f"Failed Checks: "
        f"{audit_result['failed_checks']}"
    )

    print()
    print("Audit Checks:")

    for check in checks:
        print(
            f"   {check['status']:<8} - "
            f"{check['check']}: "
            f"{check['message']}"
        )

    print()
    print("Governance Scope:")
    print("   Audit only.")
    print("   No schedule modified.")
    print("   No model artifacts modified.")
    print("   No model retrained.")
    print("   No retraining decision modified.")
    print()

    print("✓ Audit report saved:")
    print(
        f"  {OUTPUT_FILE}"
    )

    return audit_report


# ---------------------------------------------------------------------
# SCRIPT ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    run_schedule_audit()