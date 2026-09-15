"""
SupplyPrescript - AI Prediction Batch Risk Aggregation Engine

Aggregates individual AI prediction outputs into an operational
batch-level risk summary.

Supported AI Intelligence Engine structure:

{
    "shipment_id": "SHP0000001",
    "prediction": {
        "delay_probability": 0.2975,
        "prediction": "ON_TIME",
        "expected_delay_days": 0.58,
        "risk_level": "LOW"
    },
    "confidence": {
        "score": 0.2959,
        "level": "LOW"
    },
    "intelligence": {
        "score": 0.4479,
        "level": "MEDIUM"
    }
}

Input:
    ai_engine/prediction/ai_intelligence_results.json

Output:
    ai_engine/prediction/batch_risk_aggregation_report.json

This module does not modify:
    - prediction outputs
    - historical batch history
    - trained models
    - retraining decisions
    - optimization results
    - database records
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

OUTPUT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "batch_risk_aggregation_report.json"
)


def load_predictions() -> List[Dict[str, Any]]:
    """Load AI prediction records."""

    if not PREDICTION_FILE.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {PREDICTION_FILE}"
        )

    with PREDICTION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        predictions = data

    elif isinstance(data, dict):
        if isinstance(data.get("predictions"), list):
            predictions = data["predictions"]

        elif isinstance(data.get("results"), list):
            predictions = data["results"]

        elif isinstance(data.get("shipments"), list):
            predictions = data["shipments"]

        else:
            raise ValueError(
                "Prediction JSON does not contain a supported "
                "prediction list."
            )

    else:
        raise ValueError(
            "Prediction JSON must contain a list or dictionary."
        )

    if not predictions:
        raise ValueError(
            "Prediction file contains no prediction records."
        )

    return predictions


def get_prediction_section(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    """Return the nested prediction section."""

    prediction = record.get("prediction")

    if isinstance(prediction, dict):
        return prediction

    return {}


def get_confidence_section(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    """Return the nested confidence section."""

    confidence = record.get("confidence")

    if isinstance(confidence, dict):
        return confidence

    return {}


def get_intelligence_section(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    """Return the nested intelligence section."""

    intelligence = record.get("intelligence")

    if isinstance(intelligence, dict):
        return intelligence

    return {}


def get_prediction_value(
    record: Dict[str, Any],
    keys: List[str],
    default: Any = None,
) -> Any:
    """Extract a value from the nested prediction section."""

    prediction = get_prediction_section(record)

    for key in keys:
        if key in prediction:
            return prediction[key]

    for key in keys:
        target = key.lower()

        for existing_key, value in prediction.items():
            if str(existing_key).lower() == target:
                return value

    return default


def get_confidence_score(
    record: Dict[str, Any],
) -> float:
    """Extract the numeric confidence score."""

    confidence = get_confidence_section(record)

    value = confidence.get("score", 0.0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_intelligence_score(
    record: Dict[str, Any],
) -> float:
    """Extract the numeric intelligence score."""

    intelligence = get_intelligence_section(record)

    value = intelligence.get("score", 0.0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_prediction_label(
    record: Dict[str, Any],
) -> str:
    """Return the prediction label."""

    value = get_prediction_value(
        record,
        [
            "prediction",
            "PREDICTION",
        ],
        default="UNKNOWN",
    )

    if isinstance(value, dict):
        return "UNKNOWN"

    return str(value).upper()


def get_risk_level(
    record: Dict[str, Any],
) -> str:
    """Return the prediction risk level."""

    value = get_prediction_value(
        record,
        [
            "risk_level",
            "RISK_LEVEL",
        ],
        default="UNKNOWN",
    )

    if isinstance(value, dict):
        return "UNKNOWN"

    return str(value).upper()


def get_shipment_id(
    record: Dict[str, Any],
    fallback: int,
) -> str:
    """Extract shipment identifier."""

    for key in (
        "shipment_id",
        "shipmentId",
        "SHIPMENT_ID",
        "id",
        "ID",
    ):
        value = record.get(key)

        if value is not None:
            return str(value)

    return f"UNKNOWN-{fallback:04d}"


def get_numeric_prediction_value(
    record: Dict[str, Any],
    keys: List[str],
) -> float:
    """Extract numeric values from the prediction section."""

    value = get_prediction_value(
        record,
        keys,
        default=0.0,
    )

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def calculate_risk_exposure(
    delayed_percentage: float,
    critical_percentage: float,
    high_or_critical_percentage: float,
    average_delay_probability: float,
) -> float:
    """
    Calculate normalized batch risk exposure.

    Components:
        Delayed predictions       -> 25%
        Critical predictions      -> 30%
        High/Critical predictions -> 25%
        Delay probability         -> 20%

    Score range:
        0 - 100
    """

    score = (
        delayed_percentage * 0.25
        + critical_percentage * 0.30
        + high_or_critical_percentage * 0.25
        + (average_delay_probability * 100) * 0.20
    )

    return round(
        min(
            max(
                score,
                0.0,
            ),
            100.0,
        ),
        2,
    )


def classify_batch_risk(
    score: float,
) -> str:
    """Classify overall batch risk."""

    if score >= 70:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 30:
        return "MEDIUM"

    return "LOW"


def generate_recommendation(
    risk_level: str,
    delayed_percentage: float,
    critical_percentage: float,
    average_confidence: float,
) -> str:
    """Generate an operational recommendation."""

    if risk_level == "CRITICAL":
        return (
            "Immediate operational review required. "
            "Prioritize critical shipments and evaluate "
            "mitigation actions."
        )

    if risk_level == "HIGH":
        return (
            "High-risk shipments require attention. "
            "Review delayed and critical shipments before execution."
        )

    if risk_level == "MEDIUM":
        return (
            "Monitor shipment risk closely and review emerging "
            "delays before they become operationally significant."
        )

    if average_confidence < 0.40:
        return (
            "Risk level is low, but prediction confidence is limited. "
            "Monitor the next prediction batches."
        )

    return (
        "Batch risk is currently low. "
        "Continue normal monitoring of shipment predictions."
    )


def identify_highest_risk_shipments(
    predictions: List[Dict[str, Any]],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Return highest-risk shipments."""

    ranked = []

    for index, record in enumerate(
        predictions,
        start=1,
    ):
        delay_probability = get_numeric_prediction_value(
            record,
            [
                "delay_probability",
                "DELAY_PROBABILITY",
            ],
        )

        expected_delay = get_numeric_prediction_value(
            record,
            [
                "expected_delay_days",
                "EXPECTED_DELAY_DAYS",
            ],
        )

        confidence = get_confidence_score(
            record
        )

        intelligence = get_intelligence_score(
            record
        )

        risk_level = get_risk_level(
            record
        )

        risk_priority = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "UNKNOWN": 0,
        }.get(
            risk_level,
            0,
        )

        risk_score = (
            risk_priority * 25
            + delay_probability * 40
            + min(
                expected_delay / 14.0,
                1.0,
            ) * 25
            + (
                1.0
                - min(
                    max(
                        confidence,
                        0.0,
                    ),
                    1.0,
                )
            ) * 5
            + min(
                max(
                    intelligence,
                    0.0,
                ),
                1.0,
            ) * 5
        )

        ranked.append(
            {
                "shipment_id": get_shipment_id(
                    record,
                    index,
                ),
                "risk_level": risk_level,
                "prediction": get_prediction_label(
                    record
                ),
                "delay_probability": round(
                    delay_probability,
                    4,
                ),
                "expected_delay_days": round(
                    expected_delay,
                    3,
                ),
                "confidence": round(
                    confidence,
                    4,
                ),
                "intelligence": round(
                    intelligence,
                    4,
                ),
                "risk_score": round(
                    risk_score,
                    2,
                ),
            }
        )

    ranked.sort(
        key=lambda item: item["risk_score"],
        reverse=True,
    )

    return ranked[:limit]


def aggregate_predictions(
    predictions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate individual AI prediction records."""

    total_predictions = len(predictions)

    prediction_distribution = {
        "ON_TIME": 0,
        "DELAYED": 0,
        "UNKNOWN": 0,
    }

    risk_distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
        "UNKNOWN": 0,
    }

    delay_probabilities = []
    expected_delays = []
    confidence_scores = []
    intelligence_scores = []

    for record in predictions:
        prediction = get_prediction_label(
            record
        )

        risk_level = get_risk_level(
            record
        )

        if prediction in prediction_distribution:
            prediction_distribution[
                prediction
            ] += 1
        else:
            prediction_distribution[
                "UNKNOWN"
            ] += 1

        if risk_level in risk_distribution:
            risk_distribution[
                risk_level
            ] += 1
        else:
            risk_distribution[
                "UNKNOWN"
            ] += 1

        delay_probabilities.append(
            get_numeric_prediction_value(
                record,
                [
                    "delay_probability",
                    "DELAY_PROBABILITY",
                ],
            )
        )

        expected_delays.append(
            get_numeric_prediction_value(
                record,
                [
                    "expected_delay_days",
                    "EXPECTED_DELAY_DAYS",
                ],
            )
        )

        confidence_scores.append(
            get_confidence_score(
                record
            )
        )

        intelligence_scores.append(
            get_intelligence_score(
                record
            )
        )

    delayed_count = prediction_distribution[
        "DELAYED"
    ]

    critical_count = risk_distribution[
        "CRITICAL"
    ]

    high_count = risk_distribution[
        "HIGH"
    ]

    delayed_percentage = (
        delayed_count
        / total_predictions
        * 100
    )

    critical_percentage = (
        critical_count
        / total_predictions
        * 100
    )

    high_or_critical_count = (
        high_count
        + critical_count
    )

    high_or_critical_percentage = (
        high_or_critical_count
        / total_predictions
        * 100
    )

    average_delay_probability = mean(
        delay_probabilities
    )

    average_expected_delay = mean(
        expected_delays
    )

    average_confidence = mean(
        confidence_scores
    )

    average_intelligence = mean(
        intelligence_scores
    )

    risk_exposure_score = calculate_risk_exposure(
        delayed_percentage=delayed_percentage,
        critical_percentage=critical_percentage,
        high_or_critical_percentage=(
            high_or_critical_percentage
        ),
        average_delay_probability=(
            average_delay_probability
        ),
    )

    overall_risk_level = classify_batch_risk(
        risk_exposure_score
    )

    recommendation = generate_recommendation(
        risk_level=overall_risk_level,
        delayed_percentage=delayed_percentage,
        critical_percentage=critical_percentage,
        average_confidence=average_confidence,
    )

    highest_risk_shipments = (
        identify_highest_risk_shipments(
            predictions
        )
    )

    return {
        "aggregation_engine": (
            "AI Prediction Batch Risk Aggregation Engine"
        ),
        "aggregation_version": "1.3",
        "status": "COMPLETED",
        "source": str(
            PREDICTION_FILE
        ),
        "total_predictions": total_predictions,
        "prediction_distribution": {
            "ON_TIME": prediction_distribution[
                "ON_TIME"
            ],
            "DELAYED": prediction_distribution[
                "DELAYED"
            ],
            "UNKNOWN": prediction_distribution[
                "UNKNOWN"
            ],
            "ON_TIME_PERCENTAGE": round(
                prediction_distribution[
                    "ON_TIME"
                ]
                / total_predictions
                * 100,
                2,
            ),
            "DELAYED_PERCENTAGE": round(
                delayed_percentage,
                2,
            ),
        },
        "risk_distribution": {
            "LOW": risk_distribution[
                "LOW"
            ],
            "MEDIUM": risk_distribution[
                "MEDIUM"
            ],
            "HIGH": risk_distribution[
                "HIGH"
            ],
            "CRITICAL": risk_distribution[
                "CRITICAL"
            ],
            "UNKNOWN": risk_distribution[
                "UNKNOWN"
            ],
            "HIGH_OR_CRITICAL_PERCENTAGE": round(
                high_or_critical_percentage,
                2,
            ),
            "CRITICAL_PERCENTAGE": round(
                critical_percentage,
                2,
            ),
        },
        "average_metrics": {
            "delay_probability": round(
                average_delay_probability,
                4,
            ),
            "expected_delay_days": round(
                average_expected_delay,
                3,
            ),
            "confidence": round(
                average_confidence,
                4,
            ),
            "intelligence": round(
                average_intelligence,
                4,
            ),
        },
        "batch_risk": {
            "risk_exposure_score": (
                risk_exposure_score
            ),
            "overall_risk_level": (
                overall_risk_level
            ),
            "operational_recommendation": (
                recommendation
            ),
        },
        "highest_risk_shipments": (
            highest_risk_shipments
        ),
        "safety": {
            "prediction_outputs_modified": False,
            "history_modified": False,
            "models_modified": False,
            "retraining_triggered": False,
            "optimization_modified": False,
            "database_modified": False,
        },
    }


def save_report(
    report: Dict[str, Any],
) -> None:
    """Save aggregation report."""

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


def print_summary(
    report: Dict[str, Any],
) -> None:
    """Print operational aggregation summary."""

    prediction_distribution = (
        report["prediction_distribution"]
    )

    risk_distribution = (
        report["risk_distribution"]
    )

    averages = (
        report["average_metrics"]
    )

    batch_risk = (
        report["batch_risk"]
    )

    print()
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - "
        "AI PREDICTION BATCH RISK AGGREGATION ENGINE"
    )
    print("=" * 100)

    print()
    print("BATCH SUMMARY")
    print("-" * 100)

    print(
        f"Total Predictions        : "
        f"{report['total_predictions']}"
    )

    print(
        f"ON_TIME                  : "
        f"{prediction_distribution['ON_TIME']}"
    )

    print(
        f"DELAYED                  : "
        f"{prediction_distribution['DELAYED']}"
    )

    print(
        f"Delayed Percentage       : "
        f"{prediction_distribution['DELAYED_PERCENTAGE']:.2f}%"
    )

    print()
    print("RISK DISTRIBUTION")
    print("-" * 100)

    print(
        f"LOW                      : "
        f"{risk_distribution['LOW']}"
    )

    print(
        f"MEDIUM                   : "
        f"{risk_distribution['MEDIUM']}"
    )

    print(
        f"HIGH                     : "
        f"{risk_distribution['HIGH']}"
    )

    print(
        f"CRITICAL                 : "
        f"{risk_distribution['CRITICAL']}"
    )

    print(
        f"High/Critical Percentage : "
        f"{risk_distribution['HIGH_OR_CRITICAL_PERCENTAGE']:.2f}%"
    )

    print(
        f"Critical Percentage      : "
        f"{risk_distribution['CRITICAL_PERCENTAGE']:.2f}%"
    )

    print()
    print("AVERAGE AI METRICS")
    print("-" * 100)

    print(
        f"Delay Probability        : "
        f"{averages['delay_probability']:.4f}"
    )

    print(
        f"Expected Delay           : "
        f"{averages['expected_delay_days']:.3f} days"
    )

    print(
        f"Confidence               : "
        f"{averages['confidence']:.4f}"
    )

    print(
        f"Intelligence             : "
        f"{averages['intelligence']:.4f}"
    )

    print()
    print("BATCH RISK")
    print("-" * 100)

    print(
        f"Risk Exposure Score      : "
        f"{batch_risk['risk_exposure_score']:.2f}%"
    )

    print(
        f"Overall Risk Level       : "
        f"{batch_risk['overall_risk_level']}"
    )

    print(
        f"Recommendation           : "
        f"{batch_risk['operational_recommendation']}"
    )

    print()
    print("HIGHEST-RISK SHIPMENTS")
    print("-" * 100)

    for shipment in report[
        "highest_risk_shipments"
    ]:
        print(
            f"{shipment['shipment_id']} | "
            f"{shipment['risk_level']} | "
            f"{shipment['prediction']} | "
            f"Delay Prob: "
            f"{shipment['delay_probability']:.4f} | "
            f"Expected Delay: "
            f"{shipment['expected_delay_days']:.3f} days | "
            f"Confidence: "
            f"{shipment['confidence']:.4f} | "
            f"Intelligence: "
            f"{shipment['intelligence']:.4f} | "
            f"Risk Score: "
            f"{shipment['risk_score']:.2f}"
        )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 100)

    print(
        "✓ Prediction outputs were not modified."
    )

    print(
        "✓ Historical batch history was not modified."
    )

    print(
        "✓ Models were not modified."
    )

    print(
        "✓ Retraining was not triggered."
    )

    print(
        "✓ Optimization was not modified."
    )

    print(
        "✓ Database records were not modified."
    )

    print()
    print("=" * 100)

    print(
        "✓ Batch risk aggregation completed successfully."
    )

    print(
        f"✓ Report saved: {OUTPUT_FILE}"
    )

    print("=" * 100)
    print()


def main() -> None:
    """Main execution flow."""

    try:
        print(
            "Searching for AI prediction output..."
        )

        predictions = load_predictions()

        print(
            "   ✓ Prediction output loaded."
        )

        print(
            f"     {PREDICTION_FILE}"
        )

        print()
        print(
            "Aggregating prediction-level risk..."
        )

        report = aggregate_predictions(
            predictions
        )

        print(
            f"   ✓ {len(predictions)} predictions aggregated."
        )

        print()
        print(
            "Calculating batch risk exposure..."
        )

        print(
            f"   ✓ Risk exposure score: "
            f"{report['batch_risk']['risk_exposure_score']:.2f}%"
        )

        print(
            f"   ✓ Overall risk level: "
            f"{report['batch_risk']['overall_risk_level']}"
        )

        print()
        print(
            "Saving batch risk aggregation report..."
        )

        save_report(
            report
        )

        print(
            "   ✓ Report saved."
        )

        print(
            f"     {OUTPUT_FILE}"
        )

        print_summary(
            report
        )

    except FileNotFoundError as error:
        print()
        print("✗ FILE ERROR")
        print(f"  {error}")
        print()

    except json.JSONDecodeError as error:
        print()
        print("✗ JSON ERROR")
        print(
            f"  Invalid JSON: {error}"
        )
        print()

    except Exception as error:
        print()
        print(
            "✗ BATCH RISK AGGREGATION FAILED"
        )
        print(f"  {error}")
        print()


if __name__ == "__main__":
    main()