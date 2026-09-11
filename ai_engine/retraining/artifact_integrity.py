from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRAINING_DIR = PROJECT_ROOT / "ai_engine" / "retraining"
MODELS_DIR = PROJECT_ROOT / "ai_engine" / "models"

VERSION_REGISTRY_FILE = RETRAINING_DIR / "model_versions.json"

INTEGRITY_REPORT_FILE = (
    RETRAINING_DIR / "artifact_integrity_report.json"
)


MODEL_ARTIFACTS = {
    "classifier": MODELS_DIR / "classifier.json",
    "regressor": MODELS_DIR / "regressor.json",
    "classifier_metadata": MODELS_DIR / "classifier_metadata.json",
    "regressor_metadata": MODELS_DIR / "regressor_metadata.json",
}


def get_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return a dictionary."""
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
    """Save a dictionary as formatted JSON."""
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def calculate_sha256(
    file_path: Path,
) -> str:
    """
    Calculate the SHA-256 checksum of a file.

    The file is read in chunks so this also works for
    large model artifacts.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def inspect_artifact(
    artifact_name: str,
    file_path: Path,
) -> Dict[str, Any]:
    """Inspect one model artifact."""

    result = {
        "artifact": artifact_name,
        "file": str(file_path),
        "exists": False,
        "size_bytes": None,
        "sha256": None,
        "valid_json": None,
        "status": "MISSING",
    }

    if not file_path.exists():
        return result

    result["exists"] = True
    result["size_bytes"] = file_path.stat().st_size
    result["sha256"] = calculate_sha256(
        file_path
    )

    if file_path.suffix.lower() == ".json":
        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as file:
                json.load(file)

            result["valid_json"] = True
            result["status"] = "HEALTHY"

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            result["valid_json"] = False
            result["status"] = "CORRUPTED"

    else:
        result["status"] = "HEALTHY"

    return result


def inspect_all_artifacts() -> List[Dict[str, Any]]:
    """Inspect every registered model artifact."""

    results = []

    for artifact_name, file_path in MODEL_ARTIFACTS.items():
        results.append(
            inspect_artifact(
                artifact_name,
                file_path,
            )
        )

    return results


def validate_registry_consistency(
    registry: Dict[str, Any],
    artifact_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check whether the version registry and model artifacts
    are consistent.
    """

    current_version = registry.get(
        "current_version"
    )

    versions = registry.get(
        "versions",
        [],
    )

    registry_version_exists = False

    for version in versions:
        if str(
            version.get("version")
        ) == str(current_version):
            registry_version_exists = True
            break

    missing_artifacts = [
        result["artifact"]
        for result in artifact_results
        if not result["exists"]
    ]

    corrupted_artifacts = [
        result["artifact"]
        for result in artifact_results
        if result["status"] == "CORRUPTED"
    ]

    consistency_checks = {
        "current_version_defined": (
            current_version is not None
        ),
        "current_version_registered": (
            registry_version_exists
        ),
        "all_artifacts_present": (
            len(missing_artifacts) == 0
        ),
        "all_json_artifacts_valid": (
            len(corrupted_artifacts) == 0
        ),
    }

    consistency_healthy = all(
        consistency_checks.values()
    )

    return {
        "healthy": consistency_healthy,
        "checks": consistency_checks,
        "current_version": current_version,
        "missing_artifacts": missing_artifacts,
        "corrupted_artifacts": corrupted_artifacts,
    }


def calculate_overall_status(
    artifact_results: List[Dict[str, Any]],
    registry_check: Dict[str, Any],
) -> str:
    """Calculate the overall artifact health status."""

    if any(
        result["status"] == "CORRUPTED"
        for result in artifact_results
    ):
        return "CRITICAL"

    if any(
        not result["exists"]
        for result in artifact_results
    ):
        return "WARNING"

    if not registry_check.get("healthy"):
        return "WARNING"

    return "HEALTHY"


def create_integrity_report() -> Dict[str, Any]:
    """Create the complete artifact integrity report."""

    registry = load_json(
        VERSION_REGISTRY_FILE
    )

    artifact_results = inspect_all_artifacts()

    registry_check = validate_registry_consistency(
        registry,
        artifact_results,
    )

    overall_status = calculate_overall_status(
        artifact_results,
        registry_check,
    )

    healthy_count = sum(
        1
        for result in artifact_results
        if result["status"] == "HEALTHY"
    )

    missing_count = sum(
        1
        for result in artifact_results
        if result["status"] == "MISSING"
    )

    corrupted_count = sum(
        1
        for result in artifact_results
        if result["status"] == "CORRUPTED"
    )

    return {
        "system": "SupplyPrescript",
        "module": "AI Model Artifact Integrity Engine",
        "generated_at": get_timestamp(),
        "current_model_version": registry.get(
            "current_version"
        ),
        "overall_status": overall_status,
        "summary": {
            "total_artifacts": len(
                artifact_results
            ),
            "healthy_artifacts": healthy_count,
            "missing_artifacts": missing_count,
            "corrupted_artifacts": corrupted_count,
        },
        "registry_consistency": registry_check,
        "artifacts": artifact_results,
        "integrity_policy": {
            "checksum_algorithm": "SHA-256",
            "detect_missing_files": True,
            "detect_corrupted_json": True,
            "validate_registry_consistency": True,
            "modify_model_artifacts": False,
        },
    }


def print_report(
    report: Dict[str, Any],
) -> None:
    """Print the integrity report."""

    print()
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI MODEL ARTIFACT "
        "INTEGRITY ENGINE"
    )
    print("=" * 90)

    print()
    print(
        "Current Model Version:"
        f" {report.get('current_model_version')}"
    )

    print(
        "Overall Artifact Status:"
        f" {report.get('overall_status')}"
    )

    summary = report.get(
        "summary",
        {},
    )

    print()
    print("Artifact Summary:")
    print(
        f"   Total:      "
        f"{summary.get('total_artifacts')}"
    )
    print(
        f"   Healthy:    "
        f"{summary.get('healthy_artifacts')}"
    )
    print(
        f"   Missing:    "
        f"{summary.get('missing_artifacts')}"
    )
    print(
        f"   Corrupted:  "
        f"{summary.get('corrupted_artifacts')}"
    )

    print()
    print("Artifact Checks:")

    for artifact in report.get(
        "artifacts",
        [],
    ):
        print(
            f"   {artifact.get('artifact')}: "
            f"{artifact.get('status')}"
        )

        if artifact.get("size_bytes") is not None:
            print(
                f"      Size: "
                f"{artifact.get('size_bytes')} bytes"
            )

        if artifact.get("sha256"):
            print(
                f"      SHA-256: "
                f"{artifact.get('sha256')[:16]}..."
            )

    registry_check = report.get(
        "registry_consistency",
        {},
    )

    print()
    print("Registry Consistency:")

    checks = registry_check.get(
        "checks",
        {},
    )

    for check_name, check_value in checks.items():
        print(
            f"   {check_name}: "
            f"{'PASS' if check_value else 'FAIL'}"
        )

    print()
    print("=" * 90)


def main() -> None:
    """Run the artifact integrity engine."""

    print()
    print(
        "Loading model version registry..."
    )

    if not VERSION_REGISTRY_FILE.exists():
        raise FileNotFoundError(
            "Model version registry does not exist."
        )

    print(
        "   ✓ Registry found."
    )

    print()
    print(
        "Inspecting model artifacts..."
    )

    report = create_integrity_report()

    save_json(
        INTEGRITY_REPORT_FILE,
        report,
    )

    print_report(report)

    print()
    print("✓ Integrity report saved:")
    print(
        f"  {INTEGRITY_REPORT_FILE}"
    )

    print()
    print(
        "AI MODEL ARTIFACT INTEGRITY "
        "ENGINE COMPLETED"
    )


if __name__ == "__main__":
    main()