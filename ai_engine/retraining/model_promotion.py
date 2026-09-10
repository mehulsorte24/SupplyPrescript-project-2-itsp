from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRAINING_DIR = PROJECT_ROOT / "ai_engine" / "retraining"
MODELS_DIR = PROJECT_ROOT / "ai_engine" / "models"

VERSION_REGISTRY_FILE = RETRAINING_DIR / "model_versions.json"
COMPARISON_REPORT_FILE = RETRAINING_DIR / "model_comparison_report.json"

PROMOTION_REPORT_FILE = (
    RETRAINING_DIR / "model_promotion_report.json"
)

BACKUP_DIR = MODELS_DIR / "backups"


CLASSIFIER_MODEL_FILE = MODELS_DIR / "classifier.json"
REGRESSOR_MODEL_FILE = MODELS_DIR / "regressor.json"

CLASSIFIER_METADATA_FILE = (
    MODELS_DIR / "classifier_metadata.json"
)

REGRESSOR_METADATA_FILE = (
    MODELS_DIR / "regressor_metadata.json"
)


def get_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object in: {file_path}"
        )

    return data


def save_json(
    file_path: Path,
    data: Dict[str, Any],
) -> None:
    """Save JSON data."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def backup_model_artifacts(
    version: str,
) -> Dict[str, Any]:
    """
    Create backups of the currently active model artifacts.

    The current model is never deleted. Its artifacts are
    copied into a version-specific backup directory.
    """

    backup_directory = BACKUP_DIR / version
    backup_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    backed_up_files = []

    model_files = [
        CLASSIFIER_MODEL_FILE,
        REGRESSOR_MODEL_FILE,
        CLASSIFIER_METADATA_FILE,
        REGRESSOR_METADATA_FILE,
    ]

    for model_file in model_files:

        if not model_file.exists():
            continue

        destination = backup_directory / model_file.name

        shutil.copy2(
            model_file,
            destination,
        )

        backed_up_files.append(
            {
                "source": str(model_file),
                "backup": str(destination),
                "size_bytes": destination.stat().st_size,
            }
        )

    return {
        "backup_directory": str(
            backup_directory
        ),
        "files_backed_up": len(
            backed_up_files
        ),
        "files": backed_up_files,
    }


def get_current_version(
    registry: Dict[str, Any],
) -> Optional[str]:
    """Return the currently active version."""
    current_version = registry.get(
        "current_version"
    )

    if current_version is None:
        return None

    return str(current_version)


def get_candidate_version(
    comparison_report: Dict[str, Any],
) -> Optional[str]:
    """Return the candidate model version."""
    candidate_version = comparison_report.get(
        "candidate_version"
    )

    if candidate_version is None:
        return None

    return str(candidate_version)


def update_version_statuses(
    registry: Dict[str, Any],
    promoted_version: str,
) -> None:
    """Update version statuses after promotion."""

    versions = registry.get(
        "versions",
        [],
    )

    for version_record in versions:

        version_name = str(
            version_record.get(
                "version",
                "",
            )
        )

        if version_name == promoted_version:
            version_record["status"] = "ACTIVE"

        elif version_record.get("status") == "ACTIVE":
            version_record["status"] = "INACTIVE"


def promote_candidate(
    registry: Dict[str, Any],
    comparison_report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Promote a candidate model only when the comparison engine
    explicitly recommends promotion.
    """

    current_version = get_current_version(
        registry
    )

    candidate_version = get_candidate_version(
        comparison_report
    )

    decision = comparison_report.get(
        "decision",
        {},
    )

    candidate_is_better = bool(
        decision.get(
            "candidate_is_better",
            False,
        )
    )

    recommendation = decision.get(
        "recommendation",
        "KEEP_CURRENT_MODEL",
    )

    if candidate_version is None:
        return {
            "action": "NO_PROMOTION",
            "status": "REJECTED",
            "reason": "No candidate model version was provided.",
            "current_version": current_version,
            "candidate_version": None,
        }

    if candidate_version == current_version:
        return {
            "action": "NO_PROMOTION",
            "status": "BASELINE",
            "reason": (
                "Candidate version is the same as the "
                "currently active version."
            ),
            "current_version": current_version,
            "candidate_version": candidate_version,
        }

    if not candidate_is_better:
        return {
            "action": "NO_PROMOTION",
            "status": "REJECTED",
            "reason": (
                "Candidate model did not outperform "
                "the current model."
            ),
            "current_version": current_version,
            "candidate_version": candidate_version,
            "comparison_recommendation": recommendation,
        }

    if recommendation != "PROMOTE_CANDIDATE":
        return {
            "action": "NO_PROMOTION",
            "status": "REJECTED",
            "reason": (
                "Comparison engine did not authorize "
                "candidate promotion."
            ),
            "current_version": current_version,
            "candidate_version": candidate_version,
            "comparison_recommendation": recommendation,
        }

    backup_information = None

    if current_version:
        backup_information = backup_model_artifacts(
            current_version
        )

    update_version_statuses(
        registry,
        candidate_version,
    )

    registry["current_version"] = candidate_version
    registry["updated_at"] = get_timestamp()

    return {
        "action": "PROMOTE",
        "status": "PROMOTED",
        "reason": (
            "Candidate model outperformed the current "
            "model and was promoted."
        ),
        "previous_version": current_version,
        "new_active_version": candidate_version,
        "backup": backup_information,
    }


def create_promotion_report(
    registry: Dict[str, Any],
    comparison_report: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a promotion and rollback audit report."""

    promotion_result = promote_candidate(
        registry,
        comparison_report,
    )

    report = {
        "system": "SupplyPrescript",
        "module": "AI Model Promotion and Rollback Engine",
        "generated_at": get_timestamp(),
        "current_version_before_action": (
            get_current_version(registry)
            if promotion_result.get("action") != "PROMOTE"
            else promotion_result.get(
                "previous_version"
            )
        ),
        "promotion_result": promotion_result,
        "rollback": {
            "supported": True,
            "automatic_rollback": False,
            "message": (
                "Previous active model artifacts are backed up "
                "before a successful promotion."
            ),
        },
        "safety_policy": {
            "promote_only_if_candidate_is_better": True,
            "backup_previous_model": True,
            "never_delete_previous_model": True,
            "automatic_rollback": False,
        },
    }

    return report


def print_report(
    report: Dict[str, Any],
) -> None:
    """Print the promotion result."""

    print()
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - MODEL PROMOTION "
        "AND ROLLBACK ENGINE"
    )
    print("=" * 90)

    promotion_result = report.get(
        "promotion_result",
        {},
    )

    print()
    print(
        "Action:"
        f" {promotion_result.get('action')}"
    )

    print(
        "Status:"
        f" {promotion_result.get('status')}"
    )

    print()
    print(
        "Reason:"
        f" {promotion_result.get('reason')}"
    )

    previous_version = promotion_result.get(
        "previous_version"
    )

    new_version = promotion_result.get(
        "new_active_version"
    )

    current_version = promotion_result.get(
        "current_version"
    )

    candidate_version = promotion_result.get(
        "candidate_version"
    )

    if previous_version:
        print(
            f"Previous Version: "
            f"{previous_version}"
        )

    if new_version:
        print(
            f"New Active Version: "
            f"{new_version}"
        )

    if current_version:
        print(
            f"Current Version: "
            f"{current_version}"
        )

    if candidate_version:
        print(
            f"Candidate Version: "
            f"{candidate_version}"
        )

    backup = promotion_result.get(
        "backup"
    )

    if backup:
        print()
        print("Backup Information:")
        print(
            f"   Directory: "
            f"{backup.get('backup_directory')}"
        )
        print(
            f"   Files Backed Up: "
            f"{backup.get('files_backed_up')}"
        )

    print()
    print("Rollback Safety:")
    print(
        "   Previous model preserved: YES"
    )
    print(
        "   Automatic rollback: NO"
    )

    print()
    print("=" * 90)


def main() -> None:
    """Run the model promotion engine."""

    print()
    print(
        "Loading model version registry..."
    )

    registry = load_json(
        VERSION_REGISTRY_FILE
    )

    print(
        "   ✓ Registry loaded."
    )

    print()
    print(
        "Loading model comparison report..."
    )

    comparison_report = load_json(
        COMPARISON_REPORT_FILE
    )

    print(
        "   ✓ Comparison report loaded."
    )

    print()
    print(
        "Evaluating promotion decision..."
    )

    report = create_promotion_report(
        registry,
        comparison_report,
    )

    save_json(
        VERSION_REGISTRY_FILE,
        registry,
    )

    save_json(
        PROMOTION_REPORT_FILE,
        report,
    )

    print_report(report)

    print()
    print("✓ Model registry updated:")
    print(
        f"  {VERSION_REGISTRY_FILE}"
    )

    print()
    print("✓ Promotion report saved:")
    print(
        f"  {PROMOTION_REPORT_FILE}"
    )

    print()
    print(
        "MODEL PROMOTION AND ROLLBACK "
        "ENGINE COMPLETED"
    )


if __name__ == "__main__":
    main()