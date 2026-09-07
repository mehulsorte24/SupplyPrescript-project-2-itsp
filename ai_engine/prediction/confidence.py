import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path.cwd()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def calculate_confidence(delay_probability, expected_delay_days):
    probability_certainty = abs(delay_probability - 0.5) * 2

    duration_strength = min(
        max(expected_delay_days / 14.0, 0.0),
        1.0
    )

    confidence = (
        0.70 * probability_certainty
        + 0.30 * duration_strength
    )

    return round(
        min(max(confidence, 0.0), 1.0),
        4
    )


def classify_confidence(confidence_score):
    if confidence_score >= 0.75:
        return "HIGH"

    if confidence_score >= 0.50:
        return "MEDIUM"

    return "LOW"


def add_confidence_scores(predictions):
    required_columns = [
        "delay_probability",
        "expected_delay_days"
    ]

    for column in required_columns:
        if column not in predictions.columns:
            raise ValueError(
                f"Missing prediction column: {column}"
            )

    if predictions.empty:
        raise ValueError(
            "Prediction dataset contains no records."
        )

    result = predictions.copy()

    result["confidence_score"] = result.apply(
        lambda row: calculate_confidence(
            float(row["delay_probability"]),
            float(row["expected_delay_days"])
        ),
        axis=1
    )

    result["confidence_level"] = (
        result["confidence_score"]
        .apply(classify_confidence)
    )

    return result


def print_confidence_report(predictions):
    print()
    print("CONFIDENCE ANALYSIS")
    print("=" * 100)

    columns = [
        "shipment_id",
        "delay_probability",
        "prediction",
        "expected_delay_days",
        "risk_level",
        "confidence_score",
        "confidence_level"
    ]

    columns = [
        column
        for column in columns
        if column in predictions.columns
    ]

    report = predictions[columns].copy()

    if "confidence_score" in report.columns:
        report["confidence_score"] = (
            report["confidence_score"] * 100
        ).round(2)

    print(
        report.to_string(index=False)
    )

    print()
    print("=" * 100)
    print("CONFIDENCE SUMMARY")
    print("=" * 100)

    total = len(predictions)

    high = int(
        (
            predictions["confidence_level"] == "HIGH"
        ).sum()
    )

    medium = int(
        (
            predictions["confidence_level"] == "MEDIUM"
        ).sum()
    )

    low = int(
        (
            predictions["confidence_level"] == "LOW"
        ).sum()
    )

    average = predictions["confidence_score"].mean()

    print(f"Total predictions       : {total}")
    print(f"High confidence         : {high}")
    print(f"Medium confidence       : {medium}")
    print(f"Low confidence          : {low}")
    print(f"Average confidence      : {average:.2%}")


def main():
    print("=" * 100)
    print("SUPPLY PRESCRIPT - PREDICTION CONFIDENCE ENGINE")
    print("=" * 100)

    from ai_engine.prediction.predictor import (
        predict_from_dataset
    )

    input_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "ml_features.csv"
    )

    predictions = predict_from_dataset(
        str(input_file),
        limit=10
    )

    predictions_with_confidence = (
        add_confidence_scores(
            predictions
        )
    )

    print_confidence_report(
        predictions_with_confidence
    )

    print()
    print("=" * 100)
    print("PREDICTION CONFIDENCE ENGINE COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()