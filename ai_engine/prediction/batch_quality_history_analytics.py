"""
SupplyPrescript - AI Prediction Batch Quality History Analytics Engine

Purpose
-------
Analyzes the historical AI prediction batch-quality snapshots maintained by
the AI Prediction Batch Quality Trend History Engine.

The engine provides:

- Historical batch statistics
- Quality score analysis
- Confidence analysis
- Intelligence analysis
- Prediction behavior analysis
- Risk distribution analysis
- Validation analysis
- Latest-vs-baseline comparison
- Historical health assessment

Important
---------
This engine is read-only with respect to the history source.

It does NOT modify:

- AI predictions
- prediction outputs
- trained models
- model artifacts
- retraining decisions
- optimization results
- database records
- batch quality history

It only creates its own analytics report.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PREDICTION_DIR = (
    BASE_DIR / "ai_engine" / "prediction"
)

HISTORY_FILE = (
    PREDICTION_DIR / "batch_quality_history.json"
)

ANALYTICS_REPORT_FILE = (
    PREDICTION_DIR
    / "batch_quality_history_analytics_report.json"
)


# ============================================================================
# CONFIGURATION
# ============================================================================

ENGINE_NAME = (
    "AI Prediction Batch Quality History Analytics Engine"
)

ENGINE_VERSION = "1.0"

HEALTHY_QUALITY_THRESHOLD = 80.0
WARNING_QUALITY_THRESHOLD = 60.0

HEALTHY_CONFIDENCE_THRESHOLD = 0.60
WARNING_CONFIDENCE_THRESHOLD = 0.40

HEALTHY_INTELLIGENCE_THRESHOLD = 0.70
WARNING_INTELLIGENCE_THRESHOLD = 0.50

HIGH_CRITICAL_RISK_PERCENTAGE = 30.0
HIGH_DELAY_PERCENTAGE = 70.0


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_json(
    file_path: Path
) -> Dict[str, Any]:
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
            f"received {type(data).__name__}."
        )

    return data


def save_json(
    file_path: Path,
    data: Dict[str, Any]
) -> None:
    """
    Save JSON with readable formatting.
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


def percentage(
    numerator: float,
    denominator: float
) -> float:
    """
    Calculate percentage safely.
    """

    if denominator <= 0:

        return 0.0

    return (
        numerator / denominator
    ) * 100.0


def timestamp() -> str:
    """
    Return a timezone-aware ISO timestamp.
    """

    return datetime.now().astimezone().isoformat()


def average(
    values: List[float]
) -> float:
    """
    Calculate average safely.
    """

    if not values:

        return 0.0

    return sum(values) / len(values)


# ============================================================================
# HISTORY VALIDATION
# ============================================================================

def validate_history_structure(
    history: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Validate and return historical batch entries.
    """

    batches = history.get(
        "batches"
    )

    if not isinstance(
        batches,
        list
    ):

        raise ValueError(
            "History file does not contain a valid "
            "'batches' list."
        )

    valid_batches: List[Dict[str, Any]] = []

    for batch in batches:

        if isinstance(
            batch,
            dict
        ):

            valid_batches.append(
                batch
            )

    return valid_batches


# ============================================================================
# BATCH METRIC EXTRACTION
# ============================================================================

def extract_metric_series(
    batches: List[Dict[str, Any]]
) -> Dict[str, List[float]]:
    """
    Extract numerical metric series from historical batches.
    """

    return {
        "quality_scores": [
            safe_float(
                batch.get(
                    "batch_quality_score",
                    0.0
                )
            )

            for batch in batches
        ],

        "validation_scores": [
            safe_float(
                batch.get(
                    "validation_score",
                    0.0
                )
            )

            for batch in batches
        ],

        "confidence_scores": [
            safe_float(
                batch.get(
                    "average_confidence_score",
                    0.0
                )
            )

            for batch in batches
        ],

        "intelligence_scores": [
            safe_float(
                batch.get(
                    "average_intelligence_score",
                    0.0
                )
            )

            for batch in batches
        ],

        "delay_probabilities": [
            safe_float(
                batch.get(
                    "average_delay_probability",
                    0.0
                )
            )

            for batch in batches
        ],

        "expected_delay_days": [
            safe_float(
                batch.get(
                    "average_expected_delay_days",
                    0.0
                )
            )

            for batch in batches
        ],

        "delayed_percentages": [
            safe_float(
                batch.get(
                    "delayed_percentage",
                    0.0
                )
            )

            for batch in batches
        ],

        "invalid_percentages": [
            safe_float(
                batch.get(
                    "invalid_percentage",
                    0.0
                )
            )

            for batch in batches
        ],

        "critical_predictions": [
            safe_int(
                batch.get(
                    "critical_predictions",
                    0
                )
            )

            for batch in batches
        ],

        "total_predictions": [
            safe_int(
                batch.get(
                    "total_predictions",
                    0
                )
            )

            for batch in batches
        ],
    }


# ============================================================================
# HISTORICAL STATISTICS
# ============================================================================

def calculate_statistics(
    batches: List[Dict[str, Any]],
    metrics: Dict[str, List[float]]
) -> Dict[str, Any]:
    """
    Calculate aggregate historical statistics.
    """

    quality_scores = metrics[
        "quality_scores"
    ]

    validation_scores = metrics[
        "validation_scores"
    ]

    confidence_scores = metrics[
        "confidence_scores"
    ]

    intelligence_scores = metrics[
        "intelligence_scores"
    ]

    delay_probabilities = metrics[
        "delay_probabilities"
    ]

    expected_delay_days = metrics[
        "expected_delay_days"
    ]

    delayed_percentages = metrics[
        "delayed_percentages"
    ]

    invalid_percentages = metrics[
        "invalid_percentages"
    ]

    critical_predictions = metrics[
        "critical_predictions"
    ]

    total_predictions = metrics[
        "total_predictions"
    ]

    return {
        "batch_count": len(
            batches
        ),

        "total_predictions_across_batches": sum(
            total_predictions
        ),

        "quality": {
            "average": round(
                average(
                    quality_scores
                ),
                4
            ),

            "best": round(
                max(
                    quality_scores,
                    default=0.0
                ),
                4
            ),

            "lowest": round(
                min(
                    quality_scores,
                    default=0.0
                ),
                4
            ),
        },

        "validation": {
            "average_score": round(
                average(
                    validation_scores
                ),
                4
            ),

            "best_score": round(
                max(
                    validation_scores,
                    default=0.0
                ),
                4
            ),

            "lowest_score": round(
                min(
                    validation_scores,
                    default=0.0
                ),
                4
            ),
        },

        "confidence": {
            "average": round(
                average(
                    confidence_scores
                ),
                4
            ),

            "best": round(
                max(
                    confidence_scores,
                    default=0.0
                ),
                4
            ),

            "lowest": round(
                min(
                    confidence_scores,
                    default=0.0
                ),
                4
            ),
        },

        "intelligence": {
            "average": round(
                average(
                    intelligence_scores
                ),
                4
            ),

            "best": round(
                max(
                    intelligence_scores,
                    default=0.0
                ),
                4
            ),

            "lowest": round(
                min(
                    intelligence_scores,
                    default=0.0
                ),
                4
            ),
        },

        "prediction_behavior": {
            "average_delay_probability": round(
                average(
                    delay_probabilities
                ),
                4
            ),

            "average_expected_delay_days": round(
                average(
                    expected_delay_days
                ),
                4
            ),

            "average_delayed_percentage": round(
                average(
                    delayed_percentages
                ),
                4
            ),

            "average_invalid_percentage": round(
                average(
                    invalid_percentages
                ),
                4
            ),
        },

        "risk": {
            "total_critical_predictions": sum(
                critical_predictions
            ),

            "average_critical_predictions_per_batch": round(
                average(
                    critical_predictions
                ),
                4
            ),
        },
    }


# ============================================================================
# BEST / LOWEST BATCH IDENTIFICATION
# ============================================================================

def identify_extreme_batches(
    batches: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Identify best and lowest-quality historical batches.
    """

    if not batches:

        return {
            "best_batch": None,
            "lowest_quality_batch": None,
        }

    best_batch = max(
        batches,
        key=lambda batch: safe_float(
            batch.get(
                "batch_quality_score",
                0.0
            )
        )
    )

    lowest_batch = min(
        batches,
        key=lambda batch: safe_float(
            batch.get(
                "batch_quality_score",
                0.0
            )
        )
    )

    def compact_batch(
        batch: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "batch_number": safe_int(
                batch.get(
                    "batch_number",
                    0
                )
            ),

            "captured_at": batch.get(
                "captured_at"
            ),

            "quality_score": safe_float(
                batch.get(
                    "batch_quality_score",
                    0.0
                )
            ),

            "confidence_score": safe_float(
                batch.get(
                    "average_confidence_score",
                    0.0
                )
            ),

            "intelligence_score": safe_float(
                batch.get(
                    "average_intelligence_score",
                    0.0
                )
            ),

            "delayed_percentage": safe_float(
                batch.get(
                    "delayed_percentage",
                    0.0
                )
            ),

            "critical_predictions": safe_int(
                batch.get(
                    "critical_predictions",
                    0
                )
            ),
        }

    return {
        "best_batch": compact_batch(
            best_batch
        ),

        "lowest_quality_batch": compact_batch(
            lowest_batch
        ),
    }


# ============================================================================
# LATEST BATCH ANALYSIS
# ============================================================================

def analyze_latest_batch(
    batches: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze the latest historical batch.
    """

    if not batches:

        return {
            "available": False
        }

    latest = batches[-1]

    total_predictions = safe_int(
        latest.get(
            "total_predictions",
            0
        )
    )

    delayed_predictions = safe_int(
        latest.get(
            "delayed_predictions",
            0
        )
    )

    critical_predictions = safe_int(
        latest.get(
            "critical_predictions",
            0
        )
    )

    quality_score = safe_float(
        latest.get(
            "batch_quality_score",
            0.0
        )
    )

    confidence_score = safe_float(
        latest.get(
            "average_confidence_score",
            0.0
        )
    )

    intelligence_score = safe_float(
        latest.get(
            "average_intelligence_score",
            0.0
        )
    )

    if quality_score >= HEALTHY_QUALITY_THRESHOLD:

        quality_health = "HEALTHY"

    elif quality_score >= WARNING_QUALITY_THRESHOLD:

        quality_health = "WARNING"

    else:

        quality_health = "CRITICAL"

    if confidence_score >= HEALTHY_CONFIDENCE_THRESHOLD:

        confidence_health = "HEALTHY"

    elif confidence_score >= WARNING_CONFIDENCE_THRESHOLD:

        confidence_health = "WARNING"

    else:

        confidence_health = "LOW"

    if intelligence_score >= HEALTHY_INTELLIGENCE_THRESHOLD:

        intelligence_health = "HEALTHY"

    elif intelligence_score >= WARNING_INTELLIGENCE_THRESHOLD:

        intelligence_health = "WARNING"

    else:

        intelligence_health = "LOW"

    delayed_percentage = safe_float(
        latest.get(
            "delayed_percentage",
            percentage(
                delayed_predictions,
                total_predictions
            )
        )
    )

    critical_percentage = percentage(
        critical_predictions,
        total_predictions
    )

    return {
        "available": True,

        "batch_number": safe_int(
            latest.get(
                "batch_number",
                0
            )
        ),

        "captured_at": latest.get(
            "captured_at"
        ),

        "quality_score": quality_score,

        "quality_health": quality_health,

        "validation_score": safe_float(
            latest.get(
                "validation_score",
                0.0
            )
        ),

        "confidence_score": confidence_score,

        "confidence_health": confidence_health,

        "intelligence_score": intelligence_score,

        "intelligence_health": intelligence_health,

        "delay_probability": safe_float(
            latest.get(
                "average_delay_probability",
                0.0
            )
        ),

        "expected_delay_days": safe_float(
            latest.get(
                "average_expected_delay_days",
                0.0
            )
        ),

        "delayed_predictions": delayed_predictions,

        "delayed_percentage": delayed_percentage,

        "critical_predictions": critical_predictions,

        "critical_percentage": round(
            critical_percentage,
            4
        ),

        "operational_status": latest.get(
            "operational_status",
            "UNKNOWN"
        ),

        "downstream_ready": bool(
            latest.get(
                "downstream_ready",
                False
            )
        ),
    }


# ============================================================================
# BASELINE COMPARISON
# ============================================================================

def compare_latest_with_baseline(
    batches: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare the latest batch against the first historical batch.
    """

    if not batches:

        return {
            "baseline_available": False
        }

    baseline = batches[0]

    latest = batches[-1]

    def get(
        batch: Dict[str, Any],
        key: str
    ) -> float:

        return safe_float(
            batch.get(
                key,
                0.0
            )
        )

    quality_change = (
        get(
            latest,
            "batch_quality_score"
        )
        -
        get(
            baseline,
            "batch_quality_score"
        )
    )

    validation_change = (
        get(
            latest,
            "validation_score"
        )
        -
        get(
            baseline,
            "validation_score"
        )
    )

    confidence_change = (
        get(
            latest,
            "average_confidence_score"
        )
        -
        get(
            baseline,
            "average_confidence_score"
        )
    )

    intelligence_change = (
        get(
            latest,
            "average_intelligence_score"
        )
        -
        get(
            baseline,
            "average_intelligence_score"
        )
    )

    delayed_change = (
        get(
            latest,
            "delayed_percentage"
        )
        -
        get(
            baseline,
            "delayed_percentage"
        )
    )

    invalid_change = (
        get(
            latest,
            "invalid_percentage"
        )
        -
        get(
            baseline,
            "invalid_percentage"
        )
    )

    return {
        "baseline_available": True,

        "baseline_batch": safe_int(
            baseline.get(
                "batch_number",
                0
            )
        ),

        "latest_batch": safe_int(
            latest.get(
                "batch_number",
                0
            )
        ),

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

        "delayed_percentage_change": round(
            delayed_change,
            4
        ),

        "invalid_percentage_change": round(
            invalid_change,
            4
        ),
    }


# ============================================================================
# HISTORICAL HEALTH
# ============================================================================

def determine_historical_health(
    statistics: Dict[str, Any],
    latest: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determine overall historical AI batch-quality health.
    """

    if not latest.get(
        "available",
        False
    ):

        return {
            "status": "NO_DATA",

            "score": 0.0,

            "reasons": [
                "No historical batch data is available."
            ],
        }

    quality_score = safe_float(
        latest.get(
            "quality_score",
            0.0
        )
    )

    validation_score = safe_float(
        latest.get(
            "validation_score",
            0.0
        )
    )

    confidence_score = safe_float(
        latest.get(
            "confidence_score",
            0.0
        )
    )

    intelligence_score = safe_float(
        latest.get(
            "intelligence_score",
            0.0
        )
    )

    delayed_percentage = safe_float(
        latest.get(
            "delayed_percentage",
            0.0
        )
    )

    critical_percentage = safe_float(
        latest.get(
            "critical_percentage",
            0.0
        )
    )

    reasons: List[str] = []

    # Quality
    if quality_score < WARNING_QUALITY_THRESHOLD:

        reasons.append(
            "Latest batch quality score is critically low."
        )

    elif quality_score < HEALTHY_QUALITY_THRESHOLD:

        reasons.append(
            "Latest batch quality score is below the healthy threshold."
        )

    # Validation
    if validation_score < HEALTHY_QUALITY_THRESHOLD:

        reasons.append(
            "Latest validation score is below the healthy threshold."
        )

    # Confidence
    if confidence_score < WARNING_CONFIDENCE_THRESHOLD:

        reasons.append(
            "Latest AI confidence is low."
        )

    elif confidence_score < HEALTHY_CONFIDENCE_THRESHOLD:

        reasons.append(
            "Latest AI confidence is below the healthy threshold."
        )

    # Intelligence
    if intelligence_score < WARNING_INTELLIGENCE_THRESHOLD:

        reasons.append(
            "Latest AI intelligence score is low."
        )

    elif intelligence_score < HEALTHY_INTELLIGENCE_THRESHOLD:

        reasons.append(
            "Latest AI intelligence score is below the healthy threshold."
        )

    # Delayed predictions
    if delayed_percentage >= HIGH_DELAY_PERCENTAGE:

        reasons.append(
            "A high percentage of predictions are delayed."
        )

    # Critical risk
    if critical_percentage >= HIGH_CRITICAL_RISK_PERCENTAGE:

        reasons.append(
            "Critical-risk predictions represent a high percentage of the batch."
        )

    if not reasons:

        status = "HEALTHY"

    elif (
        quality_score < WARNING_QUALITY_THRESHOLD
        or
        validation_score < WARNING_QUALITY_THRESHOLD
        or
        confidence_score < WARNING_CONFIDENCE_THRESHOLD
        or
        intelligence_score < WARNING_INTELLIGENCE_THRESHOLD
    ):

        status = "CRITICAL"

    else:

        status = "WARNING"

    # Weighted health score
    quality_component = min(
        max(
            quality_score,
            0.0
        ),
        100.0
    )

    validation_component = min(
        max(
            validation_score,
            0.0
        ),
        100.0
    )

    confidence_component = min(
        max(
            confidence_score * 100.0,
            0.0
        ),
        100.0
    )

    intelligence_component = min(
        max(
            intelligence_score * 100.0,
            0.0
        ),
        100.0
    )

    health_score = (
        quality_component * 0.40
        +
        validation_component * 0.25
        +
        confidence_component * 0.15
        +
        intelligence_component * 0.20
    )

    return {
        "status": status,

        "score": round(
            health_score,
            4
        ),

        "reasons": reasons,
    }


# ============================================================================
# MAIN ANALYTICS ENGINE
# ============================================================================

def run_history_analytics() -> Dict[str, Any]:
    """
    Execute the complete historical analytics workflow.
    """

    print("=" * 100)

    print(
        "SUPPLYPRESCRIPT - "
        "AI PREDICTION BATCH QUALITY HISTORY ANALYTICS ENGINE"
    )

    print("=" * 100)

    # ------------------------------------------------------------------------
    # STEP 1 - LOAD HISTORY
    # ------------------------------------------------------------------------

    print(
        "\nSearching for batch quality history..."
    )

    try:

        history = load_json(
            HISTORY_FILE
        )

    except (
        FileNotFoundError,
        ValueError
    ) as exc:

        print(
            "   ✗ Failed to load history:"
        )

        print(
            f"     {exc}"
        )

        return {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        "   ✓ Batch quality history loaded."
    )

    print(
        f"     {HISTORY_FILE}"
    )

    # ------------------------------------------------------------------------
    # STEP 2 - VALIDATE HISTORY
    # ------------------------------------------------------------------------

    print(
        "\nValidating historical batch structure..."
    )

    try:

        batches = validate_history_structure(
            history
        )

    except ValueError as exc:

        print(
            "   ✗ History validation failed:"
        )

        print(
            f"     {exc}"
        )

        return {
            "status": "FAILED",
            "error": str(exc),
        }

    print(
        f"   ✓ Valid historical batches: "
        f"{len(batches)}"
    )

    if not batches:

        print(
            "\n   ⚠ No historical batches available."
        )

        report = {
            "engine": ENGINE_NAME,

            "version": ENGINE_VERSION,

            "generated_at": timestamp(),

            "source_history": str(
                HISTORY_FILE
            ),

            "status": "NO_DATA",

            "statistics": {},

            "latest_batch": {
                "available": False
            },

            "baseline_comparison": {
                "baseline_available": False
            },

            "historical_health": {
                "status": "NO_DATA",
                "score": 0.0,
                "reasons": [
                    "No historical batch data is available."
                ],
            },

            "operational_scope": {
                "history_modified": False,
                "predictions_modified": False,
                "models_modified": False,
                "optimization_executed": False,
                "database_modified": False,
                "analytics_only": True,
            },
        }

        save_json(
            ANALYTICS_REPORT_FILE,
            report
        )

        return report

    # ------------------------------------------------------------------------
    # STEP 3 - EXTRACT METRICS
    # ------------------------------------------------------------------------

    print(
        "\nExtracting historical metrics..."
    )

    metrics = extract_metric_series(
        batches
    )

    print(
        "   ✓ Historical metrics extracted."
    )

    # ------------------------------------------------------------------------
    # STEP 4 - CALCULATE STATISTICS
    # ------------------------------------------------------------------------

    print(
        "\nCalculating historical statistics..."
    )

    statistics = calculate_statistics(
        batches,
        metrics
    )

    print(
        "   ✓ Historical statistics calculated."
    )

    # ------------------------------------------------------------------------
    # STEP 5 - IDENTIFY EXTREME BATCHES
    # ------------------------------------------------------------------------

    print(
        "\nIdentifying best and lowest-quality batches..."
    )

    extreme_batches = identify_extreme_batches(
        batches
    )

    print(
        "   ✓ Historical extremes identified."
    )

    # ------------------------------------------------------------------------
    # STEP 6 - ANALYZE LATEST BATCH
    # ------------------------------------------------------------------------

    print(
        "\nAnalyzing latest batch..."
    )

    latest_batch = analyze_latest_batch(
        batches
    )

    print(
        "   ✓ Latest batch analysis completed."
    )

    # ------------------------------------------------------------------------
    # STEP 7 - BASELINE COMPARISON
    # ------------------------------------------------------------------------

    print(
        "\nComparing latest batch with historical baseline..."
    )

    baseline_comparison = compare_latest_with_baseline(
        batches
    )

    print(
        "   ✓ Baseline comparison completed."
    )

    # ------------------------------------------------------------------------
    # STEP 8 - HISTORICAL HEALTH
    # ------------------------------------------------------------------------

    print(
        "\nDetermining historical AI health..."
    )

    historical_health = determine_historical_health(
        statistics,
        latest_batch
    )

    print(
        "   ✓ Historical AI health determined."
    )

    # ------------------------------------------------------------------------
    # STEP 9 - BUILD REPORT
    # ------------------------------------------------------------------------

    report = {
        "engine": ENGINE_NAME,

        "version": ENGINE_VERSION,

        "generated_at": timestamp(),

        "source_history": str(
            HISTORY_FILE
        ),

        "status": "COMPLETED",

        "history_metadata": {
            "history_engine": history.get(
                "history_engine"
            ),

            "history_version": history.get(
                "history_version"
            ),

            "total_batches": len(
                batches
            ),

            "history_created_at": history.get(
                "created_at"
            ),

            "history_updated_at": history.get(
                "updated_at"
            ),
        },

        "statistics": statistics,

        "extreme_batches": extreme_batches,

        "latest_batch": latest_batch,

        "baseline_comparison": baseline_comparison,

        "historical_health": historical_health,

        "operational_scope": {
            "history_modified": False,

            "predictions_modified": False,

            "models_modified": False,

            "optimization_executed": False,

            "database_modified": False,

            "retraining_triggered": False,

            "analytics_only": True,
        },
    }

    # ------------------------------------------------------------------------
    # STEP 10 - SAVE REPORT
    # ------------------------------------------------------------------------

    print(
        "\nSaving historical analytics report..."
    )

    save_json(
        ANALYTICS_REPORT_FILE,
        report
    )

    print(
        "   ✓ Analytics report saved."
    )

    print(
        f"     {ANALYTICS_REPORT_FILE}"
    )

    # ------------------------------------------------------------------------
    # STEP 11 - DISPLAY RESULTS
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "HISTORICAL ANALYTICS SUMMARY"
    )

    print(
        "=" * 100
    )

    print(
        f"Historical Batches       : "
        f"{statistics['batch_count']}"
    )

    print(
        f"Total Predictions        : "
        f"{statistics['total_predictions_across_batches']}"
    )

    print(
        f"Average Quality Score    : "
        f"{statistics['quality']['average']:.2f}%"
    )

    print(
        f"Best Quality Score       : "
        f"{statistics['quality']['best']:.2f}%"
    )

    print(
        f"Lowest Quality Score     : "
        f"{statistics['quality']['lowest']:.2f}%"
    )

    print(
        f"Average Validation      : "
        f"{statistics['validation']['average_score']:.2f}%"
    )

    print(
        f"Average Confidence       : "
        f"{statistics['confidence']['average']:.4f}"
    )

    print(
        f"Average Intelligence     : "
        f"{statistics['intelligence']['average']:.4f}"
    )

    print(
        f"Average Delay Probability: "
        f"{statistics['prediction_behavior']['average_delay_probability']:.4f}"
    )

    print(
        f"Average Expected Delay   : "
        f"{statistics['prediction_behavior']['average_expected_delay_days']:.3f} days"
    )

    print(
        f"Average Delayed %        : "
        f"{statistics['prediction_behavior']['average_delayed_percentage']:.2f}%"
    )

    print(
        f"Total Critical          : "
        f"{statistics['risk']['total_critical_predictions']}"
    )

    # ------------------------------------------------------------------------
    # LATEST BATCH
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "LATEST BATCH"
    )

    print(
        "=" * 100
    )

    print(
        f"Batch Number             : "
        f"#{latest_batch['batch_number']}"
    )

    print(
        f"Quality Score            : "
        f"{latest_batch['quality_score']:.2f}%"
    )

    print(
        f"Quality Health           : "
        f"{latest_batch['quality_health']}"
    )

    print(
        f"Validation Score         : "
        f"{latest_batch['validation_score']:.2f}%"
    )

    print(
        f"Confidence               : "
        f"{latest_batch['confidence_score']:.4f}"
    )

    print(
        f"Confidence Health        : "
        f"{latest_batch['confidence_health']}"
    )

    print(
        f"Intelligence             : "
        f"{latest_batch['intelligence_score']:.4f}"
    )

    print(
        f"Intelligence Health      : "
        f"{latest_batch['intelligence_health']}"
    )

    print(
        f"Delay Probability        : "
        f"{latest_batch['delay_probability']:.4f}"
    )

    print(
        f"Expected Delay           : "
        f"{latest_batch['expected_delay_days']:.3f} days"
    )

    print(
        f"Delayed Predictions      : "
        f"{latest_batch['delayed_predictions']}"
    )

    print(
        f"Delayed Percentage       : "
        f"{latest_batch['delayed_percentage']:.2f}%"
    )

    print(
        f"Critical Predictions     : "
        f"{latest_batch['critical_predictions']}"
    )

    print(
        f"Critical Percentage      : "
        f"{latest_batch['critical_percentage']:.2f}%"
    )

    print(
        f"Operational Status       : "
        f"{latest_batch['operational_status']}"
    )

    print(
        f"Downstream Ready         : "
        f"{'YES' if latest_batch['downstream_ready'] else 'NO'}"
    )

    # ------------------------------------------------------------------------
    # BASELINE COMPARISON
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "BASELINE COMPARISON"
    )

    print(
        "=" * 100
    )

    print(
        f"Baseline Batch           : "
        f"#{baseline_comparison['baseline_batch']}"
    )

    print(
        f"Latest Batch             : "
        f"#{baseline_comparison['latest_batch']}"
    )

    print(
        f"Quality Change           : "
        f"{baseline_comparison['quality_score_change']:+.4f}"
    )

    print(
        f"Validation Change        : "
        f"{baseline_comparison['validation_score_change']:+.4f}"
    )

    print(
        f"Confidence Change        : "
        f"{baseline_comparison['confidence_change']:+.4f}"
    )

    print(
        f"Intelligence Change      : "
        f"{baseline_comparison['intelligence_change']:+.4f}"
    )

    print(
        f"Delayed % Change         : "
        f"{baseline_comparison['delayed_percentage_change']:+.4f}"
    )

    print(
        f"Invalid % Change         : "
        f"{baseline_comparison['invalid_percentage_change']:+.4f}"
    )

    # ------------------------------------------------------------------------
    # HEALTH
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "HISTORICAL AI HEALTH"
    )

    print(
        "=" * 100
    )

    print(
        f"Health Status            : "
        f"{historical_health['status']}"
    )

    print(
        f"Health Score             : "
        f"{historical_health['score']:.2f}%"
    )

    if historical_health["reasons"]:

        print(
            "\nHealth Signals:"
        )

        for reason in historical_health[
            "reasons"
        ]:

            print(
                f"   • {reason}"
            )

    else:

        print(
            "   ✓ No historical health warnings detected."
        )

    # ------------------------------------------------------------------------
    # FINAL STATUS
    # ------------------------------------------------------------------------

    print(
        "\n" + "=" * 100
    )

    print(
        "AI HISTORY ANALYTICS ENGINE STATUS"
    )

    print(
        "=" * 100
    )

    print(
        "✓ Historical batches analyzed."
    )

    print(
        "✓ Aggregate metrics calculated."
    )

    print(
        "✓ Latest batch analyzed."
    )

    print(
        "✓ Baseline comparison completed."
    )

    print(
        "✓ Historical AI health calculated."
    )

    print(
        "✓ Analytics report generated."
    )

    print(
        "✓ History source was not modified."
    )

    print(
        "✓ Prediction outputs were not modified."
    )

    print(
        "✓ Models were not modified."
    )

    print(
        "✓ Retraining was not triggered."
    )

    print(
        "\n" + "=" * 100
    )

    return report


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":

    result = run_history_analytics()

    if result.get(
        "status"
    ) not in (
        "COMPLETED",
        "NO_DATA"
    ):

        raise SystemExit(1)