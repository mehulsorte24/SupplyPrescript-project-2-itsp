from pathlib import Path
import sys
import json

import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
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

MODEL_DIR = (
    PROJECT_ROOT
    / "ai_engine"
    / "models"
)

MODEL_FILE = MODEL_DIR / "regressor.json"
METADATA_FILE = MODEL_DIR / "regressor_metadata.json"


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


TARGET_COLUMN = "actual_delay_days"


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
    """Prepare regression features and target."""

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

    y = pd.to_numeric(
        df[TARGET_COLUMN],
        errors="coerce",
    )

    if X.isnull().any().any():
        raise ValueError(
            "Feature dataset contains missing values."
        )

    if y.isnull().any():
        raise ValueError(
            "Regression target contains missing values."
        )

    if (y < 0).any():
        raise ValueError(
            "Regression target contains negative delay values."
        )

    return X, y


def split_data(X: pd.DataFrame, y: pd.Series):
    """Create training and testing datasets."""

    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> XGBRegressor:
    """Train the XGBoost delay-duration regression model."""

    print("\nMODEL CONFIGURATION")
    print("-" * 70)
    print("Model              : XGBoost Regressor")
    print("Objective          : reg:squarederror")
    print(f"Random state       : {RANDOM_STATE}")
    print("Number of features : 18")

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


def evaluate_model(
    model: XGBRegressor,
    X_test: pd.DataFrame,
    y_test: pd.Series,
):
    """Evaluate regression model performance."""

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

    print("\nMODEL EVALUATION")
    print("-" * 70)
    print(f"MAE                : {mae:.4f} days")
    print(f"RMSE               : {rmse:.4f} days")
    print(f"R² Score           : {r2:.4f}")

    print("\nPREDICTION SUMMARY")
    print("-" * 70)
    print(
        f"Actual mean delay      : "
        f"{y_test.mean():.2f} days"
    )
    print(
        f"Predicted mean delay   : "
        f"{predictions.mean():.2f} days"
    )
    print(
        f"Actual maximum delay   : "
        f"{y_test.max():.2f} days"
    )
    print(
        f"Predicted maximum      : "
        f"{predictions.max():.2f} days"
    )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2_score": float(r2),
    }


def print_feature_importance(
    model: XGBRegressor,
) -> None:
    """Display feature importance."""

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


def save_model(
    model: XGBRegressor,
    metrics: dict,
    feature_columns: list,
) -> None:
    """Save trained model and metadata."""

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_model(
        str(MODEL_FILE)
    )

    metadata = {
        "model_type": "XGBRegressor",
        "model_version": "1.0.0",
        "target": TARGET_COLUMN,
        "target_unit": "days",
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


def main() -> None:
    print("=" * 70)
    print("SUPPLY PRESCRIPT - XGBOOST REGRESSION TRAINING")
    print("=" * 70)

    df = load_dataset()

    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = split_data(
        X,
        y,
    )

    print("\nDATASET SPLIT")
    print("-" * 70)
    print(f"Total records    : {len(X):,}")
    print(f"Training records : {len(X_train):,}")
    print(f"Testing records  : {len(X_test):,}")

    print("\nTARGET SUMMARY")
    print("-" * 70)
    print(f"Minimum delay    : {y.min():.2f} days")
    print(f"Maximum delay    : {y.max():.2f} days")
    print(f"Average delay    : {y.mean():.2f} days")
    print(f"Median delay     : {y.median():.2f} days")

    model = train_model(
        X_train,
        y_train,
    )

    metrics = evaluate_model(
        model,
        X_test,
        y_test,
    )

    print_feature_importance(model)

    save_model(
        model,
        metrics,
        FEATURE_COLUMNS,
    )

    print("\n" + "=" * 70)
    print("XGBOOST REGRESSION TRAINING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()