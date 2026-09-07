from pathlib import Path
import sys

import pandas as pd
from xgboost import XGBClassifier, XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


CLASSIFIER_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "models"
    / "classifier.json"
)

REGRESSOR_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "models"
    / "regressor.json"
)

INPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "data"
    / "processed"
    / "ml_features.csv"
)


FEATURE_COLUMNS = [
    "distance_km",
    "lead_time_days",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "fuel_price_index",
    "warehouse_load",
    "supplier_risk",
    "weather_risk",
    "traffic_risk",
    "inventory_risk",
    "warehouse_risk",
    "distance_risk",
    "transport_risk",
    "priority_risk",
    "fuel_pressure",
    "lead_time_pressure",
    "overall_risk_score",
]


DELAY_THRESHOLD = 0.50


def load_classifier() -> XGBClassifier:
    """Load the trained XGBoost classifier."""

    if not CLASSIFIER_FILE.exists():
        raise FileNotFoundError(
            f"Classifier model not found: {CLASSIFIER_FILE}"
        )

    model = XGBClassifier()

    model.load_model(
        str(CLASSIFIER_FILE)
    )

    return model


def load_regressor() -> XGBRegressor:
    """Load the trained XGBoost regressor."""

    if not REGRESSOR_FILE.exists():
        raise FileNotFoundError(
            f"Regressor model not found: {REGRESSOR_FILE}"
        )

    model = XGBRegressor()

    model.load_model(
        str(REGRESSOR_FILE)
    )

    return model


def validate_features(
    shipment_features: pd.DataFrame,
) -> None:
    """Validate the feature input required by both models."""

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in shipment_features.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing prediction features: "
            f"{missing_columns}"
        )

    if shipment_features.empty:
        raise ValueError(
            "Prediction input contains no records."
        )

    feature_data = shipment_features[
        FEATURE_COLUMNS
    ]

    if feature_data.isnull().any().any():
        raise ValueError(
            "Prediction input contains missing values."
        )


def calculate_risk_level(
    delay_probability: float,
) -> str:
    """Convert delay probability into an operational risk level."""

    if delay_probability >= 0.80:
        return "CRITICAL"

    if delay_probability >= 0.60:
        return "HIGH"

    if delay_probability >= 0.40:
        return "MEDIUM"

    return "LOW"


def predict_shipment(
    shipment_features: pd.DataFrame,
    classifier: XGBClassifier,
    regressor: XGBRegressor,
) -> pd.DataFrame:
    """
    Generate unified AI predictions for shipment records.

    Returns:
        DataFrame containing delay probability,
        prediction, expected delay days and risk level.
    """

    validate_features(
        shipment_features
    )

    features = shipment_features[
        FEATURE_COLUMNS
    ].copy()

    delay_probabilities = (
        classifier
        .predict_proba(features)[:, 1]
    )

    predictions = [
        "DELAYED"
        if probability >= DELAY_THRESHOLD
        else "ON_TIME"
        for probability in delay_probabilities
    ]

    expected_delays = (
        regressor.predict(features)
    )

    expected_delays = [
        max(0.0, float(delay))
        for delay in expected_delays
    ]

    risk_levels = [
        calculate_risk_level(
            float(probability)
        )
        for probability in delay_probabilities
    ]

    result = pd.DataFrame(
        {
            "delay_probability": [
                round(
                    float(probability),
                    4
                )
                for probability in delay_probabilities
            ],
            "prediction": predictions,
            "expected_delay_days": [
                round(
                    delay,
                    2
                )
                for delay in expected_delays
            ],
            "risk_level": risk_levels,
        }
    )

    if "shipment_id" in shipment_features.columns:
        result.insert(
            0,
            "shipment_id",
            shipment_features[
                "shipment_id"
            ].values,
        )

    return result


def predict_from_dataset(
    input_file: str,
    limit: int = 10,
) -> pd.DataFrame:
    """Run predictions on shipment records from the feature dataset."""

    df = pd.read_csv(
        input_file
    )

    if limit <= 0:
        raise ValueError(
            "Prediction limit must be greater than zero."
        )

    sample = df.head(limit).copy()

    classifier = load_classifier()
    regressor = load_regressor()

    predictions = predict_shipment(
        sample,
        classifier,
        regressor,
    )

    return predictions


def print_prediction_report(
    predictions: pd.DataFrame,
) -> None:
    """Display prediction results."""

    print("\nPREDICTION RESULTS")
    print("=" * 90)

    display_columns = [
        column
        for column in [
            "shipment_id",
            "delay_probability",
            "prediction",
            "expected_delay_days",
            "risk_level",
        ]
        if column in predictions.columns
    ]

    print(
        predictions[
            display_columns
        ].to_string(
            index=False
        )
    )

    print("\n" + "=" * 90)
    print("PREDICTION SUMMARY")
    print("=" * 90)

    total_records = len(predictions)

    delayed_records = int(
        (
            predictions["prediction"]
            == "DELAYED"
        ).sum()
    )

    on_time_records = int(
        (
            predictions["prediction"]
            == "ON_TIME"
        ).sum()
    )

    critical_records = int(
        (
            predictions["risk_level"]
            == "CRITICAL"
        ).sum()
    )

    high_records = int(
        (
            predictions["risk_level"]
            == "HIGH"
        ).sum()
    )

    print(
        f"Total predictions     : "
        f"{total_records}"
    )

    print(
        f"Predicted delayed     : "
        f"{delayed_records}"
    )

    print(
        f"Predicted on-time     : "
        f"{on_time_records}"
    )

    print(
        f"Critical risk         : "
        f"{critical_records}"
    )

    print(
        f"High risk             : "
        f"{high_records}"
    )

    print(
        f"Average delay         : "
        f"{predictions['expected_delay_days'].mean():.2f} days"
    )

    print(
        f"Average delay risk    : "
        f"{predictions['delay_probability'].mean():.2%}"
    )


def main() -> None:
    print("=" * 90)
    print("SUPPLY PRESCRIPT - UNIFIED AI PREDICTION ENGINE")
    print("=" * 90)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {INPUT_FILE}"
        )

    predictions = predict_from_dataset(
        str(INPUT_FILE),
        limit=10,
    )

    print_prediction_report(
        predictions
    )

    print("\n" + "=" * 90)
    print("UNIFIED PREDICTION ENGINE COMPLETED")
    print("=" * 90)


if __name__ == "__main__":
    main()