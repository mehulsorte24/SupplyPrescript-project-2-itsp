from pathlib import Path
import sys
import json

import pandas as pd
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


INPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "data"
    / "processed"
    / "ml_features.csv"
)

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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "evaluation"
    / "model_evaluation_report.json"
)


RANDOM_STATE = 42
TEST_SIZE = 0.20


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


TARGET_MAPPING = {
    "ON_TIME": 0,
    "DELAYED": 1,
}


def load_dataset() -> pd.DataFrame:
    """Load the ML-ready dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded records: {len(df):,}")
    print(f"Loaded columns: {len(df.columns):,}")

    return df


def prepare_dataset(df: pd.DataFrame):
    """Prepare shared features and targets."""

    required_columns = (
        FEATURE_COLUMNS
        + [
            "delay_status",
            "actual_delay_days",
        ]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    X = df[FEATURE_COLUMNS].copy()

    y_classifier = (
        df["delay_status"]
        .map(TARGET_MAPPING)
        .astype(int)
    )

    y_regressor = pd.to_numeric(
        df["actual_delay_days"],
        errors="coerce",
    )

    if X.isnull().any().any():
        raise ValueError(
            "Feature dataset contains missing values."
        )

    if y_classifier.isnull().any():
        raise ValueError(
            "Classification target contains missing values."
        )

    if y_regressor.isnull().any():
        raise ValueError(
            "Regression target contains missing values."
        )

    return X, y_classifier, y_regressor


def split_dataset(
    X: pd.DataFrame,
    y_classifier: pd.Series,
    y_regressor: pd.Series,
):
    """Create identical train/test indices for both models."""

    indices = range(len(X))

    train_indices, test_indices = train_test_split(
        list(indices),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_classifier,
    )

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]

    y_classifier_train = y_classifier.iloc[train_indices]
    y_classifier_test = y_classifier.iloc[test_indices]

    y_regressor_train = y_regressor.iloc[train_indices]
    y_regressor_test = y_regressor.iloc[test_indices]

    return (
        X_train,
        X_test,
        y_classifier_train,
        y_classifier_test,
        y_regressor_train,
        y_regressor_test,
    )


def load_classifier() -> XGBClassifier:
    """Load the saved XGBoost classifier."""

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
    """Load the saved XGBoost regressor."""

    if not REGRESSOR_FILE.exists():
        raise FileNotFoundError(
            f"Regressor model not found: {REGRESSOR_FILE}"
        )

    model = XGBRegressor()

    model.load_model(
        str(REGRESSOR_FILE)
    )

    return model


def evaluate_classifier(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Evaluate the saved classification model."""

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    return {
        "accuracy": round(float(accuracy), 6),
        "precision": round(float(precision), 6),
        "recall": round(float(recall), 6),
        "f1_score": round(float(f1), 6),
        "roc_auc": round(float(roc_auc), 6),
        "test_records": int(len(y_test)),
        "delayed_records": int((y_test == 1).sum()),
        "on_time_records": int((y_test == 0).sum()),
    }


def evaluate_regressor(
    model: XGBRegressor,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Evaluate the saved regression model."""

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    mse = mean_squared_error(
        y_test,
        predictions,
    )

    rmse = mse ** 0.5

    r2 = r2_score(
        y_test,
        predictions,
    )

    return {
        "mae_days": round(float(mae), 6),
        "rmse_days": round(float(rmse), 6),
        "r2_score": round(float(r2), 6),
        "test_records": int(len(y_test)),
        "actual_mean_delay_days": round(
            float(y_test.mean()),
            6,
        ),
        "predicted_mean_delay_days": round(
            float(predictions.mean()),
            6,
        ),
    }


def print_classifier_report(
    metrics: dict,
) -> None:
    """Print classifier evaluation results."""

    print("\nCLASSIFICATION MODEL")
    print("-" * 70)

    print(
        f"Accuracy       : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision      : "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall         : "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"F1 Score       : "
        f"{metrics['f1_score']:.4f}"
    )

    print(
        f"ROC-AUC        : "
        f"{metrics['roc_auc']:.4f}"
    )

    print(
        f"Test records   : "
        f"{metrics['test_records']}"
    )


def print_regressor_report(
    metrics: dict,
) -> None:
    """Print regression evaluation results."""

    print("\nREGRESSION MODEL")
    print("-" * 70)

    print(
        f"MAE            : "
        f"{metrics['mae_days']:.4f} days"
    )

    print(
        f"RMSE           : "
        f"{metrics['rmse_days']:.4f} days"
    )

    print(
        f"R² Score       : "
        f"{metrics['r2_score']:.4f}"
    )

    print(
        f"Test records   : "
        f"{metrics['test_records']}"
    )

    print(
        f"Actual mean    : "
        f"{metrics['actual_mean_delay_days']:.4f} days"
    )

    print(
        f"Predicted mean : "
        f"{metrics['predicted_mean_delay_days']:.4f} days"
    )


def save_report(
    classifier_metrics: dict,
    regressor_metrics: dict,
) -> None:
    """Save structured model evaluation report."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "evaluation_version": "1.0.0",
        "dataset": {
            "records": int(
                len(
                    pd.read_csv(INPUT_FILE)
                )
            ),
            "features": len(FEATURE_COLUMNS),
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
        },
        "classification": classifier_metrics,
        "regression": regressor_metrics,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
        )

    print("\nEVALUATION ARTIFACT")
    print("-" * 70)
    print(f"Report saved: {OUTPUT_FILE}")


def main() -> None:
    print("=" * 70)
    print("SUPPLY PRESCRIPT - MODEL EVALUATION ENGINE")
    print("=" * 70)

    df = load_dataset()

    (
        X,
        y_classifier,
        y_regressor,
    ) = prepare_dataset(df)

    (
        X_train,
        X_test,
        y_classifier_train,
        y_classifier_test,
        y_regressor_train,
        y_regressor_test,
    ) = split_dataset(
        X,
        y_classifier,
        y_regressor,
    )

    print("\nEVALUATION DATASET")
    print("-" * 70)
    print(f"Total records    : {len(X):,}")
    print(f"Training records : {len(X_train):,}")
    print(f"Testing records  : {len(X_test):,}")

    classifier = load_classifier()
    regressor = load_regressor()

    classifier_metrics = evaluate_classifier(
        classifier,
        X_test,
        y_classifier_test,
    )

    regressor_metrics = evaluate_regressor(
        regressor,
        X_test,
        y_regressor_test,
    )

    print_classifier_report(
        classifier_metrics
    )

    print_regressor_report(
        regressor_metrics
    )

    save_report(
        classifier_metrics,
        regressor_metrics,
    )

    print("\n" + "=" * 70)
    print("MODEL EVALUATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()