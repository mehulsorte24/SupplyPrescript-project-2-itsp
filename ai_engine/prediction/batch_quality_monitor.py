"""
SupplyPrescript - AI Prediction Batch Quality Monitor

Purpose:
    Monitors the quality of an entire AI prediction batch.

This module:
    1. Loads unified AI prediction results.
    2. Loads the prediction validation report.
    3. Calculates batch-level quality metrics.
    4. Calculates prediction and risk distributions.
    5. Measures confidence and intelligence quality.
    6. Reads the official validation score from the validator.
    7. Produces an operational batch-quality score.
    8. Saves a monitoring report.

This module is READ-ONLY.
It does not modify predictions, models, shipment data,
or optimization decisions.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parents[2]

PREDICTION_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "ai_intelligence_results.json"
)

VALIDATION_REPORT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "prediction_validation_report.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "batch_quality_report.json"
)


VALID_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}

VALID_PREDICTIONS = {
    "ON_TIME",
    "DELAYED",
}


def load_json_file(file_path: Path) -> Any:
    """Load JSON data from a file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def calculate_average(
    values: List[float],
    decimal_places: int = 4,
) -> float:
    """Calculate an average safely."""

    if not values:
        return 0.0

    return round(
        mean(values),
        decimal_places,
    )


def validate_prediction_structure(
    prediction: Dict[str, Any],
) -> bool:
    """
    Perform a lightweight structural validation.

    Detailed validation is handled by
    response_validator.py.
    """

    if not isinstance(
        prediction,
        dict,
    ):
        return False

    shipment_id = prediction.get(
        "shipment_id"
    )

    prediction_data = prediction.get(
        "prediction"
    )

    confidence = prediction.get(
        "confidence"
    )

    intelligence = prediction.get(
        "intelligence"
    )

    risk_drivers = prediction.get(
        "risk_drivers"
    )

    shap_explanation = prediction.get(
        "shap_explanation"
    )

    historical_evidence = prediction.get(
        "historical_evidence"
    )

    if not isinstance(
        shipment_id,
        str,
    ) or not shipment_id.strip():
        return False

    if not isinstance(
        prediction_data,
        dict,
    ):
        return False

    if not isinstance(
        confidence,
        dict,
    ):
        return False

    if not isinstance(
        intelligence,
        dict,
    ):
        return False

    if not isinstance(
        risk_drivers,
        list,
    ):
        return False

    if not isinstance(
        shap_explanation,
        list,
    ):
        return False

    if not isinstance(
        historical_evidence,
        dict,
    ):
        return False

    delay_probability = prediction_data.get(
        "delay_probability"
    )

    prediction_status = prediction_data.get(
        "prediction"
    )

    expected_delay_days = prediction_data.get(
        "expected_delay_days"
    )

    risk_level = prediction_data.get(
        "risk_level"
    )

    confidence_score = confidence.get(
        "score"
    )

    intelligence_score = intelligence.get(
        "score"
    )

    if not isinstance(
        delay_probability,
        (int, float),
    ):
        return False

    if not 0 <= delay_probability <= 1:
        return False

    if prediction_status not in VALID_PREDICTIONS:
        return False

    if not isinstance(
        expected_delay_days,
        (int, float),
    ):
        return False

    if expected_delay_days < 0:
        return False

    if risk_level not in VALID_RISK_LEVELS:
        return False

    if not isinstance(
        confidence_score,
        (int, float),
    ):
        return False

    if not 0 <= confidence_score <= 1:
        return False

    if not isinstance(
        intelligence_score,
        (int, float),
    ):
        return False

    if not 0 <= intelligence_score <= 1:
        return False

    return True


def extract_validation_quality(
    validation_report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract official validation metrics.

    Actual validator structure:

        validation
        ├── validation_status
        ├── validation_score
        ├── total_shipments
        ├── valid_shipments
        ├── invalid_shipments
        ├── total_checks
        ├── passed_checks
        ├── failed_checks
        └── shipment_results
    """

    validation = validation_report.get(
        "validation",
        {}
    )

    if not isinstance(
        validation,
        dict,
    ):
        return {
            "validation_status": "UNKNOWN",
            "validation_score": 0.0,
            "total_shipments": 0,
            "valid_shipments": 0,
            "invalid_shipments": 0,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "shipment_results": [],
        }

    shipment_results = validation.get(
        "shipment_results",
        []
    )

    if not isinstance(
        shipment_results,
        list,
    ):
        shipment_results = []

    return {
        "validation_status": validation.get(
            "validation_status",
            "UNKNOWN",
        ),
        "validation_score": float(
            validation.get(
                "validation_score",
                0.0,
            )
        ),
        "total_shipments": int(
            validation.get(
                "total_shipments",
                len(shipment_results),
            )
        ),
        "valid_shipments": int(
            validation.get(
                "valid_shipments",
                0,
            )
        ),
        "invalid_shipments": int(
            validation.get(
                "invalid_shipments",
                0,
            )
        ),
        "total_checks": int(
            validation.get(
                "total_checks",
                0,
            )
        ),
        "passed_checks": int(
            validation.get(
                "passed_checks",
                0,
            )
        ),
        "failed_checks": int(
            validation.get(
                "failed_checks",
                0,
            )
        ),
        "shipment_results": shipment_results,
    }


def calculate_risk_distribution(
    predictions: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Calculate prediction counts by risk level."""

    distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    for item in predictions:

        risk_level = (
            item
            .get("prediction", {})
            .get("risk_level")
        )

        if risk_level in distribution:
            distribution[risk_level] += 1

    return distribution


def calculate_prediction_distribution(
    predictions: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Calculate ON_TIME and DELAYED counts."""

    distribution = {
        "ON_TIME": 0,
        "DELAYED": 0,
    }

    for item in predictions:

        prediction_status = (
            item
            .get("prediction", {})
            .get("prediction")
        )

        if prediction_status in distribution:
            distribution[prediction_status] += 1

    return distribution


def calculate_quality_score(
    validation_score: float,
    valid_percentage: float,
    average_confidence: float,
    average_intelligence: float,
) -> float:
    """
    Calculate the overall batch quality score.

    Weighting:

        Validation quality  = 40%
        Structural validity = 25%
        Confidence          = 20%
        Intelligence        = 15%
    """

    score = (
        validation_score * 0.40
        + valid_percentage * 0.25
        + average_confidence * 100 * 0.20
        + average_intelligence * 100 * 0.15
    )

    return round(
        score,
        2,
    )


def determine_quality_level(
    quality_score: float,
) -> str:
    """Convert quality score into a quality level."""

    if quality_score >= 90:
        return "EXCELLENT"

    if quality_score >= 75:
        return "GOOD"

    if quality_score >= 60:
        return "WARNING"

    return "POOR"


def determine_operational_safety(
    valid_count: int,
    total_count: int,
    invalid_count: int,
) -> str:
    """Determine downstream operational safety."""

    if total_count == 0:
        return "UNSAFE"

    validity_percentage = (
        valid_count
        / total_count
    ) * 100

    if (
        invalid_count == 0
        and validity_percentage == 100
    ):
        return "SAFE"

    if validity_percentage >= 95:
        return "SAFE_WITH_WARNINGS"

    return "UNSAFE"


def build_batch_quality_report(
    predictions: List[Dict[str, Any]],
    validation_report: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the complete batch quality report."""

    total_predictions = len(
        predictions
    )

    valid_predictions = sum(
        validate_prediction_structure(item)
        for item in predictions
    )

    invalid_predictions = (
        total_predictions
        - valid_predictions
    )

    if total_predictions > 0:

        valid_percentage = round(
            (
                valid_predictions
                / total_predictions
            )
            * 100,
            2,
        )

    else:

        valid_percentage = 0.0

    delay_probabilities = []
    expected_delay_days = []
    confidence_scores = []
    intelligence_scores = []

    for item in predictions:

        prediction_data = item.get(
            "prediction",
            {}
        )

        confidence_data = item.get(
            "confidence",
            {}
        )

        intelligence_data = item.get(
            "intelligence",
            {}
        )

        delay_probability = (
            prediction_data.get(
                "delay_probability"
            )
        )

        expected_delay = (
            prediction_data.get(
                "expected_delay_days"
            )
        )

        confidence_score = (
            confidence_data.get(
                "score"
            )
        )

        intelligence_score = (
            intelligence_data.get(
                "score"
            )
        )

        if isinstance(
            delay_probability,
            (int, float),
        ):
            delay_probabilities.append(
                delay_probability
            )

        if isinstance(
            expected_delay,
            (int, float),
        ):
            expected_delay_days.append(
                expected_delay
            )

        if isinstance(
            confidence_score,
            (int, float),
        ):
            confidence_scores.append(
                confidence_score
            )

        if isinstance(
            intelligence_score,
            (int, float),
        ):
            intelligence_scores.append(
                intelligence_score
            )

    risk_distribution = (
        calculate_risk_distribution(
            predictions
        )
    )

    prediction_distribution = (
        calculate_prediction_distribution(
            predictions
        )
    )

    validation_quality = (
        extract_validation_quality(
            validation_report
        )
    )

    validation_score = (
        validation_quality[
            "validation_score"
        ]
    )

    average_delay_probability = (
        calculate_average(
            delay_probabilities
        )
    )

    average_expected_delay = (
        calculate_average(
            expected_delay_days
        )
    )

    average_confidence = (
        calculate_average(
            confidence_scores
        )
    )

    average_intelligence = (
        calculate_average(
            intelligence_scores
        )
    )

    quality_score = calculate_quality_score(
        validation_score=validation_score,
        valid_percentage=valid_percentage,
        average_confidence=average_confidence,
        average_intelligence=average_intelligence,
    )

    quality_level = (
        determine_quality_level(
            quality_score
        )
    )

    operational_safety = (
        determine_operational_safety(
            valid_count=valid_predictions,
            total_count=total_predictions,
            invalid_count=invalid_predictions,
        )
    )

    delayed_count = (
        prediction_distribution[
            "DELAYED"
        ]
    )

    on_time_count = (
        prediction_distribution[
            "ON_TIME"
        ]
    )

    if total_predictions > 0:

        delayed_percentage = round(
            (
                delayed_count
                / total_predictions
            )
            * 100,
            2,
        )

        on_time_percentage = round(
            (
                on_time_count
                / total_predictions
            )
            * 100,
            2,
        )

    else:

        delayed_percentage = 0.0
        on_time_percentage = 0.0

    return {
        "monitor_name": (
            "AI Prediction Batch Quality Monitor"
        ),
        "monitor_version": "1.0",
        "status": "COMPLETED",
        "total_predictions": (
            total_predictions
        ),
        "valid_predictions": (
            valid_predictions
        ),
        "invalid_predictions": (
            invalid_predictions
        ),
        "valid_percentage": (
            valid_percentage
        ),
        "validation_quality": {
            "validation_status": (
                validation_quality[
                    "validation_status"
                ]
            ),
            "validation_score": (
                validation_score
            ),
            "total_shipments": (
                validation_quality[
                    "total_shipments"
                ]
            ),
            "valid_shipments": (
                validation_quality[
                    "valid_shipments"
                ]
            ),
            "invalid_shipments": (
                validation_quality[
                    "invalid_shipments"
                ]
            ),
            "total_checks": (
                validation_quality[
                    "total_checks"
                ]
            ),
            "passed_checks": (
                validation_quality[
                    "passed_checks"
                ]
            ),
            "failed_checks": (
                validation_quality[
                    "failed_checks"
                ]
            ),
        },
        "average_delay_probability": (
            average_delay_probability
        ),
        "average_expected_delay_days": (
            average_expected_delay
        ),
        "average_confidence_score": (
            average_confidence
        ),
        "average_intelligence_score": (
            average_intelligence
        ),
        "prediction_distribution": {
            "ON_TIME": on_time_count,
            "DELAYED": delayed_count,
            "ON_TIME_PERCENTAGE": (
                on_time_percentage
            ),
            "DELAYED_PERCENTAGE": (
                delayed_percentage
            ),
        },
        "risk_distribution": (
            risk_distribution
        ),
        "batch_quality": {
            "score": quality_score,
            "level": quality_level,
        },
        "operational_safety": {
            "status": operational_safety,
            "downstream_ready": (
                operational_safety
                in {
                    "SAFE",
                    "SAFE_WITH_WARNINGS",
                }
            ),
        },
    }


def save_report(
    report: Dict[str, Any],
) -> None:
    """Save the batch quality report."""

    OUTPUT_FILE.parent.mkdir(
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
            indent=2,
        )


def print_report(
    report: Dict[str, Any],
) -> None:
    """Print a readable monitoring summary."""

    print()
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - "
        "AI PREDICTION BATCH QUALITY MONITOR"
    )
    print("=" * 100)

    print()
    print("BATCH SUMMARY")
    print("-" * 100)

    print(
        f"Total Predictions       : "
        f"{report['total_predictions']}"
    )

    print(
        f"Valid Predictions       : "
        f"{report['valid_predictions']}"
    )

    print(
        f"Invalid Predictions     : "
        f"{report['invalid_predictions']}"
    )

    print(
        f"Valid Percentage        : "
        f"{report['valid_percentage']:.2f}%"
    )

    print()
    print("VALIDATION QUALITY")
    print("-" * 100)

    validation = report[
        "validation_quality"
    ]

    print(
        f"Validation Status       : "
        f"{validation['validation_status']}"
    )

    print(
        f"Validation Score        : "
        f"{validation['validation_score']:.2f}%"
    )

    print(
        f"Total Shipments         : "
        f"{validation['total_shipments']}"
    )

    print(
        f"Valid Shipments         : "
        f"{validation['valid_shipments']}"
    )

    print(
        f"Invalid Shipments       : "
        f"{validation['invalid_shipments']}"
    )

    print(
        f"Total Checks            : "
        f"{validation['total_checks']}"
    )

    print(
        f"Passed Checks           : "
        f"{validation['passed_checks']}"
    )

    print(
        f"Failed Checks           : "
        f"{validation['failed_checks']}"
    )

    print()
    print("QUALITY METRICS")
    print("-" * 100)

    print(
        f"Average Delay Prob.     : "
        f"{report['average_delay_probability']:.4f}"
    )

    print(
        f"Average Expected Delay  : "
        f"{report['average_expected_delay_days']:.2f} days"
    )

    print(
        f"Average Confidence      : "
        f"{report['average_confidence_score']:.4f}"
    )

    print(
        f"Average Intelligence    : "
        f"{report['average_intelligence_score']:.4f}"
    )

    print()
    print("PREDICTION DISTRIBUTION")
    print("-" * 100)

    prediction_distribution = report[
        "prediction_distribution"
    ]

    print(
        f"ON_TIME                 : "
        f"{prediction_distribution['ON_TIME']}"
    )

    print(
        f"DELAYED                 : "
        f"{prediction_distribution['DELAYED']}"
    )

    print(
        f"ON_TIME Percentage      : "
        f"{prediction_distribution['ON_TIME_PERCENTAGE']:.2f}%"
    )

    print(
        f"DELAYED Percentage      : "
        f"{prediction_distribution['DELAYED_PERCENTAGE']:.2f}%"
    )

    print()
    print("RISK DISTRIBUTION")
    print("-" * 100)

    for risk_level, count in report[
        "risk_distribution"
    ].items():

        print(
            f"{risk_level:<24}: {count}"
        )

    print()
    print("BATCH QUALITY")
    print("-" * 100)

    print(
        f"Quality Score           : "
        f"{report['batch_quality']['score']:.2f}%"
    )

    print(
        f"Quality Level           : "
        f"{report['batch_quality']['level']}"
    )

    print()
    print("DOWNSTREAM SAFETY")
    print("-" * 100)

    safety_status = report[
        "operational_safety"
    ]["status"]

    downstream_ready = report[
        "operational_safety"
    ]["downstream_ready"]

    if downstream_ready:

        print(
            "   ✓ AI prediction batch is ready "
            "for downstream consumption."
        )

    else:

        print(
            "   ✗ AI prediction batch requires "
            "quality attention."
        )

    print(
        f"Safety Status           : "
        f"{safety_status}"
    )

    print()
    print("✓ Batch quality report saved:")
    print(
        f"  {OUTPUT_FILE}"
    )

    print()


def main() -> None:
    """Run the AI prediction batch quality monitor."""

    print()
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - "
        "AI PREDICTION BATCH QUALITY MONITOR"
    )
    print("=" * 100)

    print()
    print(
        "Searching for AI prediction output..."
    )

    try:

        predictions = load_json_file(
            PREDICTION_FILE
        )

        if not isinstance(
            predictions,
            list,
        ):

            raise ValueError(
                "AI prediction output must be a JSON list."
            )

        print(
            "   ✓ Prediction output loaded."
        )

        print(
            f"     {PREDICTION_FILE}"
        )

    except Exception as error:

        print(
            f"   ✗ Failed to load predictions: "
            f"{error}"
        )

        return

    print()
    print(
        f"Found {len(predictions)} "
        f"prediction records."
    )

    print()
    print(
        "Loading prediction validation report..."
    )

    try:

        validation_report = load_json_file(
            VALIDATION_REPORT_FILE
        )

        print(
            "   ✓ Validation report loaded."
        )

    except Exception as error:

        print(
            f"   ⚠ Validation report unavailable: "
            f"{error}"
        )

        validation_report = {}

    print()
    print(
        "Analyzing complete prediction batch..."
    )

    report = build_batch_quality_report(
        predictions=predictions,
        validation_report=validation_report,
    )

    save_report(report)

    print_report(report)


if __name__ == "__main__":
    main()