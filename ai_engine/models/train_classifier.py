from pathlib import Path
import sys
import json

import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
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

MODEL_DIR = (
    PROJECT_ROOT
    / "ai_engine"
    / "models"
)

MODEL_FILE = MODEL_DIR / "classifier.json"
METADATA_FILE = MODEL_DIR / "classifier_metadata.json"


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


TARGET_COLUMN = "delay_status"

TARGET_MAPPING = {
    "ON_TIME": 0,
    "DELAYED": 1,
}


def load_dataset() -> pd.DataFrame:
    """Load the ML-ready shipment dataset."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"ML feature dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded records: {len(df):,}")
    print(f"Loaded columns: {len(df.columns):,}")

    return df


def prepare_data(df: pd.DataFrame):
    """Prepare features and binary classification target."""

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

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

    y = (
        df[TARGET_COLUMN]
        .map(TARGET_MAPPING)
        .astype(int)
    )

    if X.isnull().any().any():
        raise ValueError(
            "Feature dataset contains missing values."
        )

    if y.isnull().any():
        raise ValueError(
            "Target contains missing values."
        )

    return X, y


def split_data(X: pd.DataFrame, y: pd.Series):
    """Create stratified training and testing datasets."""

    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> XGBClassifier:
    """Train the XGBoost delay classification model."""

    delayed_count = int((y_train == 1).sum())
    on_time_count = int((y_train == 0).sum())

    if delayed_count == 0:
        raise ValueError(
            "Training data contains no delayed shipments."
        )

    scale_pos_weight = (
        on_time_count / delayed_count
    )

    print("\nMODEL CONFIGURATION")
    print("-" * 70)
    print("Model              : XGBoost Classifier")
    print("Objective          : binary:logistic")
    print(f"Random state       : {RANDOM_STATE}")
    print(f"Scale pos weight   : {scale_pos_weight:.4f}")
    print("Number of features : 18")

    model = XGBClassifier(
        objective="binary:logistic",
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    return model


def evaluate_model(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
):
    """Evaluate classifier performance."""

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
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

    auc = roc_auc_score(
        y_test,
        probabilities
    )

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    print("\nMODEL EVALUATION")
    print("-" * 70)
    print(f"Accuracy           : {accuracy:.4f}")
    print(f"Precision          : {precision:.4f}")
    print(f"Recall             : {recall:.4f}")
    print(f"F1 Score           : {f1:.4f}")
    print(f"ROC-AUC            : {auc:.4f}")

    print("\nCONFUSION MATRIX")
    print("-" * 70)
    print(matrix)

    print("\nCLASSIFICATION REPORT")
    print("-" * 70)
    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "ON_TIME",
                "DELAYED",
            ],
            zero_division=0,
        )
    )

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "confusion_matrix": matrix.tolist(),
    }


def save_model(
    model: XGBClassifier,
    metrics: dict,
    feature_columns: list,
) -> None:
    """Save trained model and metadata."""

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model.save_model(
        str(MODEL_FILE)
    )

    metadata = {
        "model_type": "XGBClassifier",
        "model_version": "1.0.0",
        "target": TARGET_COLUMN,
        "target_mapping": TARGET_MAPPING,
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "metrics": metrics,
    }

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
        )

    print("\nMODEL ARTIFACTS")
    print("-" * 70)
    print(f"Model saved    : {MODEL_FILE}")
    print(f"Metadata saved : {METADATA_FILE}")


def print_feature_importance(
    model: XGBClassifier,
) -> None:
    """Display feature importance for model interpretation."""

    importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    )

    importance = importance.sort_values(
        by="importance",
        ascending=False,
    )

    print("\nTOP FEATURE IMPORTANCE")
    print("-" * 70)

    for _, row in importance.head(10).iterrows():
        print(
            f"{row['feature']:<25} "
            f"{row['importance']:.6f}"
        )


def main() -> None:
    print("=" * 70)
    print("SUPPLY PRESCRIPT - XGBOOST CLASSIFICATION TRAINING")
    print("=" * 70)

    df = load_dataset()

    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = split_data(
        X,
        y
    )

    print("\nDATASET SPLIT")
    print("-" * 70)
    print(f"Total records    : {len(X):,}")
    print(f"Training records : {len(X_train):,}")
    print(f"Testing records  : {len(X_test):,}")

    model = train_model(
        X_train,
        y_train
    )

    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    print_feature_importance(model)

    save_model(
        model,
        metrics,
        FEATURE_COLUMNS
    )

    print("\n" + "=" * 70)
    print("XGBOOST CLASSIFICATION TRAINING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()