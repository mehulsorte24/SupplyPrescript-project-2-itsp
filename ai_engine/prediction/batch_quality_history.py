"""
SupplyPrescript - AI Prediction Batch Quality Trend History Engine

Purpose
-------
Maintains a historical record of AI prediction batch-quality snapshots.

The engine reads the latest batch quality trend report and appends a
compact snapshot to a historical JSON file.

It tracks:

- Total predictions
- Valid and invalid predictions
- Validation quality
- Delay probability
- Expected delay duration
- Confidence
- Intelligence
- Prediction distribution
- Risk distribution
- Batch quality score
- Operational safety
- Historical quality movement

Important
---------
This engine does not modify:

- prediction results
- trained models
- model artifacts
- optimization results
- database records
- retraining decisions

It only maintains its own historical monitoring file.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PREDICTION_DIR = BASE_DIR / "ai_engine" / "prediction"

TREND_REPORT_FILE = (
    PREDICTION_DIR / "batch_quality_trend_report.json"
)

HISTORY_FILE = (
    PREDICTION_DIR / "batch_quality_history.json"
)


# ============================================================================
# CONFIGURATION
# ============================================================================

HISTORY_VERSION = "1.0"

QUALITY_DEGRADATION_THRESHOLD = -5.0
VALIDATION_DEGRADATION_THRESHOLD = -5.0
CONFIDENCE_DEGRADATION_THRESHOLD = -0.10
INTELLIGENCE_DEGRADATION_THRESHOLD = -0.10

INVALID_PERCENTAGE_INCREASE_THRESHOLD = 5.0
CRITICAL_RISK_INCREASE_THRESHOLD = 2
DELAYED_PREDICTION_INCREASE_THRESHOLD = 2


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load a JSON object from disk.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    try:
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in file: {file_path}\n"
            f"Error: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object in {file_path}, "
            f"but received {type(data).__name__}."
        )

    return data


def save_json(
    file_path: Path,
    data: Dict[str, Any]
) -> None:
    """
    Save JSON using readable indentation.
    """

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with file_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=2
        )


def safe_float(
    value: Any,
    default: float = 0.0
) -> float:
    """
    Safely convert a value to float.
    """

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):
        return default


def safe_int(
    value: Any,
    default: int = 0
) -> int:
    """
    Safely convert a value to integer.
    """

    try:
        return int(value)

    except (
        TypeError,
        ValueError
    ):
        return default


def timestamp() -> str:
    """
    Return a timezone-aware local ISO timestamp.
    """

    return datetime.now().astimezone().isoformat()


def numeric_change(
    current: float,
    previous: float
) -> float:
    """
    Calculate direct numeric change.
    """

    return current - previous


# ============================================================================
# CURRENT REPORT EXTRACTION
# ============================================================================

def extract_batch_snapshot(
    report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extract the current batch metrics from the actual
    batch_quality_trend_report.json structure.

    Expected structure:

        current_batch
        validation_quality
        prediction_quality
        prediction_distribution
        risk_distribution
        batch_quality
        current_batch_health
        operational_safety
    """

    current_batch = report.get(
        "current_batch",
        {}
    )

    validation_quality = report.get(
        "validation_quality",
        {}
    )

    prediction_quality = report.get(
        "prediction_quality",
        {}
    )

    prediction_distribution = report.get(
        "prediction_distribution",
        {}
    )

    risk_distribution = report.get(
        "risk_distribution",
        {}
    )

    batch_quality = report.get(
        "batch_quality",
        {}
    )

    current_batch_health = report.get(
        "current_batch_health",
        {}
    )

    operational_safety = report.get(
        "operational_safety",
        {}
    )

    total_predictions = safe_int(
        current_batch.get(
            "total_predictions",
            0
        )
    )

    valid_predictions = safe_int(
        current_batch.get(
            "valid_predictions",
            0
        )
    )

    invalid_predictions = safe_int(
        current_batch.get(
            "invalid_predictions",
            0
        )
    )

    invalid_percentage = safe_float(
        current_batch.get(
            "invalid_percentage",
            0.0
        )
    )

    valid_percentage = safe_float(
        current_batch.get(
            "valid_percentage",
            0.0
        )
    )

    delayed_predictions = safe_int(
        prediction_distribution.get(
            "DELAYED",
            0
        )
    )

    critical_predictions = safe_int(
        risk_distribution.get(
            "CRITICAL",
            0
        )
    )

    snapshot = {
        "captured_at": timestamp(),

        "total_predictions": total_predictions,

        "valid_predictions": valid_predictions,

        "invalid_predictions": invalid_predictions,

        "valid_percentage": valid_percentage,

        "invalid_percentage": invalid_percentage,

        "validation": {
            "status": validation_quality.get(
                "validation_status",
                current_batch_health.get(
                    "validation_status",
                    "UNKNOWN"
                )
            ),

            "score": safe_float(
                validation_quality.get(
                    "validation_score",
                    current_batch_health.get(
                        "validation_score",
                        0.0
                    )
                )
            ),

            "total_checks": safe_int(
                validation_quality.get(
                    "total_checks",
                    0
                )
            ),

            "passed_checks": safe_int(
                validation_quality.get(
                    "passed_checks",
                    0
                )
            ),

            "failed_checks": safe_int(
                validation_quality.get(
                    "failed_checks",
                    0
                )
            ),
        },

        "prediction_quality": {
            "average_delay_probability": safe_float(
                prediction_quality.get(
                    "average_delay_probability",
                    0.0
                )
            ),

            "average_expected_delay_days": safe_float(
                prediction_quality.get(
                    "average_expected_delay_days",
                    0.0
                )
            ),

            "average_confidence_score": safe_float(
                prediction_quality.get(
                    "average_confidence_score",
                    0.0
                )
            ),

            "average_intelligence_score": safe_float(
                prediction_quality.get(
                    "average_intelligence_score",
                    0.0
                )
            ),
        },

        "prediction_distribution": {
            "ON_TIME": safe_int(
                prediction_distribution.get(
                    "ON_TIME",
                    0
                )
            ),

            "DELAYED": delayed_predictions,

            "ON_TIME_PERCENTAGE": safe_float(
                prediction_distribution.get(
                    "ON_TIME_PERCENTAGE",
                    0.0
                )
            ),

            "DELAYED_PERCENTAGE": safe_float(
                prediction_distribution.get(
                    "DELAYED_PERCENTAGE",
                    0.0
                )
            ),
        },

        "risk_distribution": {
            "LOW": safe_int(
                risk_distribution.get(
                    "LOW",
                    0
                )
            ),

            "MEDIUM": safe_int(
                risk_distribution.get(
                    "MEDIUM",
                    0
                )
            ),

            "HIGH": safe_int(
                risk_distribution.get(
                    "HIGH",
                    0
                )
            ),

            "CRITICAL": critical_predictions,
        },

        "batch_quality": {
            "score": safe_float(
                batch_quality.get(
                    "score",
                    current_batch_health.get(
                        "quality_score",
                        0.0
                    )
                )
            ),

            "level": batch_quality.get(
                "level",
                current_batch_health.get(
                    "quality_level",
                    "UNKNOWN"
                )
            ),
        },

        "operational_safety": {
            "status": operational_safety.get(
                "status",
                current_batch_health.get(
                    "safety_status",
                    "UNKNOWN"
                )
            ),

            "downstream_ready": bool(
                operational_safety.get(
                    "downstream_ready",
                    current_batch_health.get(
                        "downstream_ready",
                        False
                    )
                )
            ),
        },
    }

    return snapshot


# ============================================================================
# HISTORY STRUCTURE
# ============================================================================

def create_empty_history() -> Dict[str, Any]:
    """
    Create a new empty history document.
    """

    return {
        "history_engine": (
            "AI Prediction Batch Quality Trend History Engine"
        ),

        "history_version": HISTORY_VERSION,

        "created_at": timestamp(),

        "updated_at": timestamp(),

        "total_batches": 0,

        "batches": [],
    }


def load_history() -> Dict[str, Any]:
    """
    Load existing history.

    If no history exists, create an empty history structure.
    """

    if not HISTORY_FILE.exists():
        return create_empty_history()

    try:
        history = load_json(
            HISTORY_FILE
        )

    except (
        FileNotFoundError,
        ValueError
    ):
        return create_empty_history()

    if not isinstance(
        history.get("batches"),
        list
    ):
        history["batches"] = []

    history.setdefault(
        "history_engine",
        "AI Prediction Batch Quality Trend History Engine"
    )

    history.setdefault(
        "history_version",
        HISTORY_VERSION
    )

    history.setdefault(
        "created_at",
        timestamp()
    )

    history["updated_at"] = timestamp()

    history["total_batches"] = len(
        history["batches"]
    )

    return history


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

def build_snapshot_fingerprint(
    snapshot: Dict[str, Any]
) -> tuple:
    """
    Build a compact fingerprint from important metrics.
    """

    return (
        snapshot["total_predictions"],

        snapshot["valid_predictions"],

        snapshot["invalid_predictions"],

        round(
            snapshot["batch_quality"]["score"],
            6
        ),

        round(
            snapshot["validation"]["score"],
            6
        ),

        round(
            snapshot["prediction_quality"][
                "average_confidence_score"
            ],
            6
        ),

        round(
            snapshot["prediction_quality"][
                "average_intelligence_score"
            ],
            6
        ),

        snapshot["prediction_distribution"][
            "DELAYED"
        ],

        snapshot["risk_distribution"][
            "CRITICAL"
        ],
    )


def build_history_fingerprint(
    entry: Dict[str, Any]
) -> tuple:
    """
    Build the same fingerprint format from a history entry.
    """

    return (
        safe_int(
            entry.get(
                "total_predictions",
                0
            )
        ),

        safe_int(
            entry.get(
                "valid_predictions",
                0
            )
        ),

        safe_int(
            entry.get(
                "invalid_predictions",
                0
            )
        ),

        round(
            safe_float(
                entry.get(
                    "batch_quality_score",
                    0.0
                )
            ),
            6
        ),

        round(
            safe_float(
                entry.get(
                    "validation_score",
                    0.0
                )
            ),
            6
        ),

        round(
            safe_float(
                entry.get(
                    "average_confidence_score",
                    0.0
                )
            ),
            6
        ),

        round(
            safe_float(
                entry.get(
                    "average_intelligence_score",
                    0.0
                )
            ),
            6
        ),

        safe_int(
            entry.get(
                "delayed_predictions",
                0
            )
        ),

        safe_int(
            entry.get(
                "critical_predictions",
                0
            )
        ),
    )


def is_duplicate_snapshot(
    history: Dict[str, Any],
    snapshot: Dict[str, Any]
) -> bool:
    """
    Determine whether the current snapshot already exists.
    """

    current_fingerprint = build_snapshot_fingerprint(
        snapshot
    )

    for previous in history.get(
        "batches",
        []
    ):

        previous_fingerprint = build_history_fingerprint(
            previous
        )

        if current_fingerprint == previous_fingerprint:
            return True

    return False


# ============================================================================
# HISTORY ENTRY
# ============================================================================

def create_history_entry(
    snapshot: Dict[str, Any],
    batch_number: int
) -> Dict[str, Any]:
    """
    Convert the current snapshot into a compact historical entry.
    """

    return {
        "batch_number": batch_number,

        "captured_at": snapshot[
            "captured_at"
        ],

        "total_predictions": snapshot[
            "total_predictions"
        ],

        "valid_predictions": snapshot[
            "valid_predictions"
        ],

        "invalid_predictions": snapshot[
            "invalid_predictions"
        ],

        "valid_percentage": snapshot[
            "valid_percentage"
        ],

        "invalid_percentage": snapshot[
            "invalid_percentage"
        ],

        "validation_score": snapshot[
            "validation"
        ]["score"],

        "validation_status": snapshot[
            "validation"
        ]["status"],

        "total_validation_checks": snapshot[
            "validation"
        ]["total_checks"],

        "passed_validation_checks": snapshot[
            "validation"
        ]["passed_checks"],

        "failed_validation_checks": snapshot[
            "validation"
        ]["failed_checks"],

        "average_delay_probability": snapshot[
            "prediction_quality"
        ]["average_delay_probability"],

        "average_expected_delay_days": snapshot[
            "prediction_quality"
        ]["average_expected_delay_days"],

        "average_confidence_score": snapshot[
            "prediction_quality"
        ]["average_confidence_score"],

        "average_intelligence_score": snapshot[
            "prediction_quality"
        ]["average_intelligence_score"],

        "on_time_predictions": snapshot[
            "prediction_distribution"
        ]["ON_TIME"],

        "delayed_predictions": snapshot[
            "prediction_distribution"
        ]["DELAYED"],

        "on_time_percentage": snapshot[
            "prediction_distribution"
        ]["ON_TIME_PERCENTAGE"],

        "delayed_percentage": snapshot[
            "prediction_distribution"
        ]["DELAYED_PERCENTAGE"],

        "low_risk_predictions": snapshot[
            "risk_distribution"
        ]["LOW"],

        "medium_risk_predictions": snapshot[
            "risk_distribution"
        ]["MEDIUM"],

        "high_risk_predictions": snapshot[
            "risk_distribution"
        ]["HIGH"],

        "critical_predictions": snapshot[
            "risk_distribution"
        ]["CRITICAL"],

        "batch_quality_score": snapshot[
            "batch_quality"
        ]["score"],

        "batch_quality_level": snapshot[
            "batch_quality"
        ]["level"],

        "operational_status": snapshot[
            "operational_safety"
        ]["status"],

        "downstream_ready": snapshot[
            "operational_safety"
        ]["downstream_ready"],
    }


# ============================================================================
# TREND ANALYSIS
# ============================================================================

def get_previous_entry(
    history: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Return the batch immediately before the latest batch.
    """

    batches = history.get(
        "batches",
        []
    )

    if len(batches) < 2:
        return None

    return batches[-2]


def calculate_trend(
    current: Dict[str, Any],
    previous: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare current batch with previous batch.

    If no previous batch exists, return BASELINE.
    """

    if previous is None:

        return {
            "status": "BASELINE",

            "direction": "NO_PREVIOUS_BATCH",

            "quality_score_change": 0.0,

            "validation_score_change": 0.0,

            "confidence_change": 0.0,

            "intelligence_change": 0.0,

            "invalid_percentage_change": 0.0,

            "critical_risk_change": 0,

            "delayed_prediction_change": 0,

            "degradation_detected": False,

            "degradation_reasons": [],
        }

    current_quality = safe_float(
        current.get(
            "batch_quality_score",
            0.0
        )
    )

    previous_quality = safe_float(
        previous.get(
            "batch_quality_score",
            0.0
        )
    )

    current_validation = safe_float(
        current.get(
            "validation_score",
            0.0
        )
    )

    previous_validation = safe_float(
        previous.get(
            "validation_score",
            0.0
        )
    )

    current_confidence = safe_float(
        current.get(
            "average_confidence_score",
            0.0
        )
    )

    previous_confidence = safe_float(
        previous.get(
            "average_confidence_score",
            0.0
        )
    )

    current_intelligence = safe_float(
        current.get(
            "average_intelligence_score",
            0.0
        )
    )

    previous_intelligence = safe_float(
        previous.get(
            "average_intelligence_score",
            0.0
        )
    )

    current_invalid_percentage = safe_float(
        current.get(
            "invalid_percentage",
            0.0
        )
    )

    previous_invalid_percentage = safe_float(
        previous.get(
            "invalid_percentage",
            0.0
        )
    )

    current_critical = safe_int(
        current.get(
            "critical_predictions",
            0
        )
    )

    previous_critical = safe_int(
        previous.get(
            "critical_predictions",
            0
        )
    )

    current_delayed = safe_int(
        current.get(
            "delayed_predictions",
            0
        )
    )

    previous_delayed = safe_int(
        previous.get(
            "delayed_predictions",
            0
        )
    )

    quality_change = numeric_change(
        current_quality,
        previous_quality
    )

    validation_change = numeric_change(
        current_validation,
        previous_validation
    )

    confidence_change = numeric_change(
        current_confidence,
        previous_confidence
    )

    intelligence_change = numeric_change(
        current_intelligence,
        previous_intelligence
    )

    invalid_percentage_change = numeric_change(
        current_invalid_percentage,
        previous_invalid_percentage
    )

    critical_change = (
        current_critical -
        previous_critical
    )

    delayed_change = (
        current_delayed -
        previous_delayed
    )

    degradation_reasons: List[str] = []

    if quality_change <= QUALITY_DEGRADATION_THRESHOLD:

        degradation_reasons.append(
            "Batch quality score decreased significantly."
        )

    if (
        validation_change
        <= VALIDATION_DEGRADATION_THRESHOLD
    ):

        degradation_reasons.append(
            "Validation score decreased significantly."
        )

    if (
        confidence_change
        <= CONFIDENCE_DEGRADATION_THRESHOLD
    ):

        degradation_reasons.append(
            "Average confidence score decreased significantly."
        )

    if (
        intelligence_change
        <= INTELLIGENCE_DEGRADATION_THRESHOLD
    ):

        degradation_reasons.append(
            "Average intelligence score decreased significantly."
        )

    if (
        invalid_percentage_change
        >= INVALID_PERCENTAGE_INCREASE_THRESHOLD
    ):

        degradation_reasons.append(
            "Invalid prediction percentage increased significantly."
        )

    if (
        critical_change
        >= CRITICAL_RISK_INCREASE_THRESHOLD
    ):

        degradation_reasons.append(
            "Critical-risk prediction count increased significantly."
        )

    if (
        delayed_change
        >= DELAYED_PREDICTION_INCREASE_THRESHOLD
    ):

        degradation_reasons.append(
            "Delayed prediction count increased significantly."
        )

    degradation_detected = bool(
        degradation_reasons
    )

    positive_signals = 0

    negative_signals = 0

    if quality_change > 0:

        positive_signals += 1

    elif quality_change < 0:

        negative_signals += 1

    if validation_change > 0:

        positive_signals += 1

    elif validation_change < 0:

        negative_signals += 1

    if confidence_change > 0:

        positive_signals += 1

    elif confidence_change < 0:

        negative_signals += 1

    if intelligence_change > 0:

        positive_signals += 1

    elif intelligence_change < 0:

        negative_signals += 1

    if degradation_detected:

        direction = "DEGRADING"

        status = "DEGRADED"

    elif positive_signals > negative_signals:

        direction = "IMPROVING"

        status = "IMPROVED"

    elif negative_signals > positive_signals:

        direction = "DECLINING"

        status = "DECLINING"

    else:

        direction = "STABLE"

        status = "STABLE"

    return {
        "status": status,

        "direction": direction,

        "quality_score_change": round(
            quality_change,
            4
        ),

        "validation_score_change": round(
            validation_change,
            4
        ),

        "confidence_change": round(
            confidence_change,
            4
        ),

        "intelligence_change": round(
            intelligence_change,
            4
        ),

        "invalid_percentage_change": round(
            invalid_percentage_change,
            4
        ),

        "critical_risk_change": critical_change,

        "delayed_prediction_change": delayed_change,

        "degradation_detected": degradation_detected,

        "degradation_reasons": degradation_reasons,

        "positive_signals": positive_signals,

        "negative_signals": negative_signals,
    }


# ============================================================================
# HISTORICAL SUMMARY
# ============================================================================

def calculate_history_summary(
    history: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate summary statistics from historical batches.
    """

    batches = history.get(
        "batches",
        []
    )

    if not batches:

        return {
            "batches_available": 0,

            "average_quality_score": 0.0,

            "best_quality_score": 0.0,

            "lowest_quality_score": 0.0,

            "average_confidence_score": 0.0,

            "average_intelligence_score": 0.0,

            "degraded_batches": 0,

            "improved_batches": 0,

            "stable_batches": 0,
        }

    quality_scores = [
        safe_float(
            batch.get(
                "batch_quality_score",
                0.0
            )
        )

        for batch in batches
    ]

    confidence_scores = [
        safe_float(
            batch.get(
                "average_confidence_score",
                0.0
            )
        )

        for batch in batches
    ]

    intelligence_scores = [
        safe_float(
            batch.get(
                "average_intelligence_score",
                0.0
            )
        )

        for batch in batches
    ]

    degraded_batches = 0

    improved_batches = 0

    stable_batches = 0

    for index in range(
        1,
        len(batches)
    ):

        current = batches[index]

        previous = batches[index - 1]

        quality_change = (
            safe_float(
                current.get(
                    "batch_quality_score",
                    0.0
                )
            )
            -
            safe_float(
                previous.get(
                    "batch_quality_score",
                    0.0
                )
            )
        )

        if (
            quality_change
            <= QUALITY_DEGRADATION_THRESHOLD
        ):

            degraded_batches += 1

        elif quality_change > 0:

            improved_batches += 1

        else:

            stable_batches += 1

    return {
        "batches_available": len(
            batches
        ),

        "average_quality_score": round(
            sum(quality_scores)
            /
            len(quality_scores),
            4
        ),

        "best_quality_score": round(
            max(quality_scores),
            4
        ),

        "lowest_quality_score": round(
            min(quality_scores),
            4
        ),

        "average_confidence_score": round(
            sum(confidence_scores)
            /
            len(confidence_scores),
            4
        ),

        "average_intelligence_score": round(
            sum(intelligence_scores)
            /
            len(intelligence_scores),
            4
        ),

        "degraded_batches": degraded_batches,

        "improved_batches": improved_batches,

        "stable_batches": stable_batches,
    }


# ============================================================================
# MAIN ENGINE
# ============================================================================

def run_history_engine() -> Dict[str, Any]:
    """
    Execute the complete batch-quality history workflow.
    """

    print("=" * 100)

    print(
        "SUPPLYPRESCRIPT - "
        "AI PREDICTION BATCH QUALITY TREND HISTORY ENGINE"
    )

    print("=" * 100)

    # ------------------------------------------------------------------------
    # STEP 1 - LOAD CURRENT TREND REPORT
    # ------------------------------------------------------------------------

    print(
        "\nSearching for batch quality trend report..."
    )

    try:

        trend_report = load_json(
            TREND_REPORT_FILE
        )

    except (
        FileNotFoundError,
        ValueError
    ) as exc:

        print(
            "   ✗ Failed to load trend report:"
        )

        print(
            f"     {exc}"
        )

        return {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        "   ✓ Batch quality trend report loaded."
    )

    print(
        f"     {TREND_REPORT_FILE}"
    )

    # ------------------------------------------------------------------------
    # STEP 2 - EXTRACT CURRENT SNAPSHOT
    # ------------------------------------------------------------------------

    print(
        "\nExtracting current batch snapshot..."
    )

    try:

        snapshot = extract_batch_snapshot(
            trend_report
        )

    except Exception as exc:

        print(
            "   ✗ Failed to extract batch snapshot."
        )

        print(
            f"     {exc}"
        )

        return {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        "   ✓ Current batch metrics extracted."
    )

    print(
        f"     Predictions: "
        f"{snapshot['total_predictions']}"
    )

    print(
        f"     Quality Score: "
        f"{snapshot['batch_quality']['score']:.2f}%"
    )

    print(
        f"     Validation Score: "
        f"{snapshot['validation']['score']:.2f}%"
    )

    print(
        f"     Confidence: "
        f"{snapshot['prediction_quality']['average_confidence_score']:.4f}"
    )

    print(
        f"     Intelligence: "
        f"{snapshot['prediction_quality']['average_intelligence_score']:.4f}"
    )

    # ------------------------------------------------------------------------
    # STEP 3 - LOAD HISTORY
    # ------------------------------------------------------------------------

    print(
        "\nLoading batch quality history..."
    )

    history = load_history()

    previous_batch_count = len(
        history.get(
            "batches",
            []
        )
    )

    print(
        f"   ✓ Existing historical batches: "
        f"{previous_batch_count}"
    )

    # ------------------------------------------------------------------------
    # STEP 4 - DUPLICATE CHECK
    # ------------------------------------------------------------------------

    print(
        "\nChecking for duplicate batch snapshot..."
    )

    duplicate = is_duplicate_snapshot(
        history,
        snapshot
    )

    if duplicate:

        print(
            "   ⚠ Current batch snapshot already "
            "exists in history."
        )

        print(
            "   ✓ No duplicate history entry will be created."
        )

        latest_entry = (
            history.get(
                "batches",
                []
            )[-1]
            if history.get(
                "batches"
            )
            else None
        )

        previous_entry = (
            get_previous_entry(history)
            if previous_batch_count >= 2
            else None
        )

        if latest_entry is not None:

            trend = calculate_trend(
                latest_entry,
                previous_entry
            )

        else:

            trend = calculate_trend(
                create_history_entry(
                    snapshot,
                    previous_batch_count
                ),
                None
            )

        history_summary = calculate_history_summary(
            history
        )

        return {
            "status": "COMPLETED",

            "duplicate": True,

            "history_file": str(
                HISTORY_FILE
            ),

            "total_batches": len(
                history.get(
                    "batches",
                    []
                )
            ),

            "trend": trend,

            "history_summary": history_summary,
        }

    # ------------------------------------------------------------------------
    # STEP 5 - CREATE HISTORY ENTRY
    # ------------------------------------------------------------------------

    print(
        "\nCreating historical batch entry..."
    )

    batch_number = (
        previous_batch_count + 1
    )

    history_entry = create_history_entry(
        snapshot,
        batch_number
    )

    history.setdefault(
        "batches",
        []
    ).append(
        history_entry
    )

    history["total_batches"] = len(
        history["batches"]
    )

    history["updated_at"] = timestamp()

    print(
        f"   ✓ Batch #{batch_number} added to history."
    )

    # ------------------------------------------------------------------------
    # STEP 6 - TREND ANALYSIS
    # ------------------------------------------------------------------------

    print(
        "\nAnalyzing historical quality trend..."
    )

    previous_entry = (
        history["batches"][-2]
        if len(
            history["batches"]
        ) >= 2
        else None
    )

    trend = calculate_trend(
        history_entry,
        previous_entry
    )

    # ------------------------------------------------------------------------
    # STEP 7 - HISTORY SUMMARY
    # ------------------------------------------------------------------------

    history_summary = calculate_history_summary(
        history
    )

    # ------------------------------------------------------------------------
    # STEP 8 - SAVE HISTORY
    # ------------------------------------------------------------------------

    print(
        "\nSaving batch quality history..."
    )

    save_json(
        HISTORY_FILE,
        history
    )

    print(
        "   ✓ Batch quality history saved."
    )

    print(
        f"     {HISTORY_FILE}"
    )

    # ------------------------------------------------------------------------
    # STEP 9 - DISPLAY CURRENT HISTORY
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "CURRENT HISTORY STATUS"
    )

    print(
        "=" * 100
    )

    print(
        f"Total Historical Batches : "
        f"{history['total_batches']}"
    )

    print(
        f"Current Batch            : "
        f"#{batch_number}"
    )

    print(
        f"Predictions              : "
        f"{history_entry['total_predictions']}"
    )

    print(
        f"Valid Predictions        : "
        f"{history_entry['valid_predictions']}"
    )

    print(
        f"Invalid Predictions      : "
        f"{history_entry['invalid_predictions']}"
    )

    print(
        f"Quality Score            : "
        f"{history_entry['batch_quality_score']:.2f}%"
    )

    print(
        f"Validation Score         : "
        f"{history_entry['validation_score']:.2f}%"
    )

    print(
        f"Confidence Score         : "
        f"{history_entry['average_confidence_score']:.4f}"
    )

    print(
        f"Intelligence Score       : "
        f"{history_entry['average_intelligence_score']:.4f}"
    )

    print(
        f"Delayed Predictions      : "
        f"{history_entry['delayed_predictions']}"
    )

    print(
        f"Critical Predictions     : "
        f"{history_entry['critical_predictions']}"
    )

    # ------------------------------------------------------------------------
    # STEP 10 - TREND RESULTS
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "TREND ANALYSIS"
    )

    print(
        "=" * 100
    )

    print(
        f"Trend Status             : "
        f"{trend['status']}"
    )

    print(
        f"Trend Direction          : "
        f"{trend['direction']}"
    )

    print(
        f"Quality Score Change     : "
        f"{trend['quality_score_change']:+.4f}"
    )

    print(
        f"Validation Change        : "
        f"{trend['validation_score_change']:+.4f}"
    )

    print(
        f"Confidence Change        : "
        f"{trend['confidence_change']:+.4f}"
    )

    print(
        f"Intelligence Change      : "
        f"{trend['intelligence_change']:+.4f}"
    )

    print(
        f"Invalid % Change         : "
        f"{trend['invalid_percentage_change']:+.4f}"
    )

    print(
        f"Critical Risk Change     : "
        f"{trend['critical_risk_change']:+d}"
    )

    print(
        f"Delayed Prediction Δ     : "
        f"{trend['delayed_prediction_change']:+d}"
    )

    print(
        f"Degradation Detected     : "
        f"{'YES' if trend['degradation_detected'] else 'NO'}"
    )

    if trend["degradation_reasons"]:

        print(
            "\nDegradation Reasons:"
        )

        for reason in trend[
            "degradation_reasons"
        ]:

            print(
                f"   • {reason}"
            )

    # ------------------------------------------------------------------------
    # STEP 11 - HISTORICAL SUMMARY
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "HISTORICAL SUMMARY"
    )

    print(
        "=" * 100
    )

    print(
        f"Batches Available        : "
        f"{history_summary['batches_available']}"
    )

    print(
        f"Average Quality Score    : "
        f"{history_summary['average_quality_score']:.2f}%"
    )

    print(
        f"Best Quality Score       : "
        f"{history_summary['best_quality_score']:.2f}%"
    )

    print(
        f"Lowest Quality Score     : "
        f"{history_summary['lowest_quality_score']:.2f}%"
    )

    print(
        f"Average Confidence       : "
        f"{history_summary['average_confidence_score']:.4f}"
    )

    print(
        f"Average Intelligence     : "
        f"{history_summary['average_intelligence_score']:.4f}"
    )

    print(
        f"Improved Batches         : "
        f"{history_summary['improved_batches']}"
    )

    print(
        f"Degraded Batches         : "
        f"{history_summary['degraded_batches']}"
    )

    print(
        f"Stable Batches           : "
        f"{history_summary['stable_batches']}"
    )

    # ------------------------------------------------------------------------
    # STEP 12 - FINAL STATUS
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "AI BATCH HISTORY ENGINE STATUS"
    )

    print(
        "=" * 100
    )

    print(
        "✓ Historical batch snapshot recorded."
    )

    print(
        "✓ Duplicate protection active."
    )

    print(
        "✓ Trend comparison completed."
    )

    print(
        "✓ Historical summary calculated."
    )

    print(
        "✓ No prediction data was modified."
    )

    print(
        "✓ No model artifacts were modified."
    )

    print(
        "✓ No retraining was triggered."
    )

    print(
        "\n" + "=" * 100
    )

    return {
        "status": "COMPLETED",

        "duplicate": False,

        "history_file": str(
            HISTORY_FILE
        ),

        "total_batches": history[
            "total_batches"
        ],

        "current_batch": batch_number,

        "trend": trend,

        "history_summary": history_summary,
    }


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":

    result = run_history_engine()

    if result.get(
        "status"
    ) != "COMPLETED":

        raise SystemExit(1)