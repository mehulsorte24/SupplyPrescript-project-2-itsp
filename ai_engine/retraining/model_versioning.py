from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRAINING_DIR = PROJECT_ROOT / "ai_engine" / "retraining"

VERSION_REGISTRY_FILE = RETRAINING_DIR / "model_versions.json"

CLASSIFIER_MODEL_FILE = (
    PROJECT_ROOT / "ai_engine" / "models" / "classifier.json"
)

REGRESSOR_MODEL_FILE = (
    PROJECT_ROOT / "ai_engine" / "models" / "regressor.json"
)

CLASSIFIER_METADATA_FILE = (
    PROJECT_ROOT / "ai_engine" / "models" / "classifier_metadata.json"
)

REGRESSOR_METADATA_FILE = (
    PROJECT_ROOT / "ai_engine" / "models" / "regressor_metadata.json"
)


def get_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def ensure_registry() -> None:
    """Create the model version registry if it does not exist."""
    RETRAINING_DIR.mkdir(parents=True, exist_ok=True)

    if not VERSION_REGISTRY_FILE.exists():
        initial_registry = {
            "system": "SupplyPrescript",
            "module": "AI Model Versioning Engine",
            "created_at": get_timestamp(),
            "current_version": None,
            "versions": [],
        }

        with open(VERSION_REGISTRY_FILE, "w", encoding="utf-8") as file:
            json.dump(initial_registry, file, indent=2)


def load_registry() -> Dict[str, Any]:
    """Load the model version registry."""
    ensure_registry()

    try:
        with open(VERSION_REGISTRY_FILE, "r", encoding="utf-8") as file:
            registry = json.load(file)

        if not isinstance(registry, dict):
            raise ValueError("Model version registry must contain a JSON object.")

        registry.setdefault("system", "SupplyPrescript")
        registry.setdefault("module", "AI Model Versioning Engine")
        registry.setdefault("created_at", get_timestamp())
        registry.setdefault("current_version", None)
        registry.setdefault("versions", [])

        return registry

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in model version registry: {error}"
        ) from error


def save_registry(registry: Dict[str, Any]) -> None:
    """Save the model version registry."""
    RETRAINING_DIR.mkdir(parents=True, exist_ok=True)

    with open(VERSION_REGISTRY_FILE, "w", encoding="utf-8") as file:
        json.dump(registry, file, indent=2)


def get_next_version(registry: Dict[str, Any]) -> str:
    """Generate the next semantic model version."""
    versions: List[Dict[str, Any]] = registry.get("versions", [])

    if not versions:
        return "v1.0"

    version_numbers = []

    for version in versions:
        version_name = str(version.get("version", ""))

        if version_name.startswith("v"):
            try:
                number = float(version_name[1:])
                version_numbers.append(number)
            except ValueError:
                continue

    if not version_numbers:
        return "v1.0"

    next_version = max(version_numbers) + 0.1

    return f"v{next_version:.1f}"


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """Return basic metadata for a model artifact."""
    if not file_path.exists():
        return {
            "file": file_path.name,
            "exists": False,
            "size_bytes": None,
        }

    return {
        "file": file_path.name,
        "exists": True,
        "size_bytes": file_path.stat().st_size,
    }


def load_model_metrics(metadata_file: Path) -> Dict[str, Any]:
    """Load training metadata when available."""
    if not metadata_file.exists():
        return {}

    try:
        with open(metadata_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        if isinstance(metadata, dict):
            return metadata

    except (json.JSONDecodeError, OSError):
        pass

    return {}


def create_version_record(
    registry: Dict[str, Any],
    version_status: str = "ACTIVE",
) -> Dict[str, Any]:
    """Create a version record for the currently available models."""
    version = get_next_version(registry)

    classifier_metadata = load_model_metrics(CLASSIFIER_METADATA_FILE)
    regressor_metadata = load_model_metrics(REGRESSOR_METADATA_FILE)

    version_record = {
        "version": version,
        "created_at": get_timestamp(),
        "status": version_status,
        "models": {
            "classifier": get_file_metadata(CLASSIFIER_MODEL_FILE),
            "regressor": get_file_metadata(REGRESSOR_MODEL_FILE),
        },
        "training_metadata": {
            "classifier": classifier_metadata,
            "regressor": regressor_metadata,
        },
    }

    return version_record


def register_current_models() -> Dict[str, Any]:
    """Register the currently available classifier and regressor."""
    registry = load_registry()

    versions: List[Dict[str, Any]] = registry.get("versions", [])

    if versions:
        print("Existing model versions found.")
        print(f"Current registered version: {registry.get('current_version')}")
        return registry

    print("No model versions found.")
    print("Registering the current baseline models...")

    version_record = create_version_record(registry)

    registry["versions"].append(version_record)
    registry["current_version"] = version_record["version"]
    registry["updated_at"] = get_timestamp()

    save_registry(registry)

    return registry


def print_registry(registry: Dict[str, Any]) -> None:
    """Display the current model version registry."""
    print()
    print("=" * 90)
    print("SUPPLYPRESCRIPT - MODEL VERSIONING ENGINE")
    print("=" * 90)

    print()
    print("System:")
    print(f"   {registry.get('system')}")

    print("Module:")
    print(f"   {registry.get('module')}")

    print("Current Model Version:")
    print(f"   {registry.get('current_version')}")

    versions = registry.get("versions", [])

    print()
    print(f"Registered Versions: {len(versions)}")

    for version in versions:
        print()
        print(f"   Version: {version.get('version')}")
        print(f"   Status: {version.get('status')}")
        print(f"   Created: {version.get('created_at')}")

        classifier = version.get("models", {}).get("classifier", {})
        regressor = version.get("models", {}).get("regressor", {})

        print(
            f"   Classifier: "
            f"{'Available' if classifier.get('exists') else 'Missing'}"
        )

        print(
            f"   Regressor: "
            f"{'Available' if regressor.get('exists') else 'Missing'}"
        )

    print()
    print("=" * 90)


def main() -> None:
    """Run the model versioning engine."""
    try:
        registry = register_current_models()

        print_registry(registry)

        print()
        print("✓ Model version registry saved:")
        print(f"  {VERSION_REGISTRY_FILE}")

        print()
        print("MODEL VERSIONING ENGINE COMPLETED")

    except Exception as error:
        print()
        print("✗ Model versioning failed:")
        print(f"  {error}")
        raise


if __name__ == "__main__":
    main()