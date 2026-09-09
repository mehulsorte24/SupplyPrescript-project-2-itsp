from pathlib import Path
import json
from datetime import datetime, timezone

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from xgboost import XGBClassifier, XGBRegressor


PROJECT_ROOT = Path.cwd()

TRIGGER_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_trigger.json"
)

FEATURE_FILE = (
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
    / "retraining"
    / "retraining_report.json"
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


def load_json(file_path):
    """Load JSON data."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_training_data():
    """Load and validate ML training data."""

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {FEATURE_FILE}"
        )

    df = pd.read_csv(
        FEATURE_FILE
    )

    missing_features = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    required_targets = [
        "delay_status",
        "actual_delay_days",
    ]

    missing_targets = [
        column
        for column in required_targets
        if column not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing feature columns: "
            + ", ".join(missing_features)
        )

    if missing_targets:
        raise ValueError(
            "Missing target columns: "
            + ", ".join(missing_targets)
        )

    df = df.dropna(
        subset=FEATURE_COLUMNS + required_targets
    ).copy()

    if len(df) < 20:
        raise ValueError(
            "At least 20 valid records are required "
            "for retraining."
        )

    return df


def prepare_targets(df):
    """Prepare classification and regression targets."""

    classification_target = (
        df["delay_status"]
        .astype(str)
        .str.upper()
        .eq("DELAYED")
        .astype(int)
    )

    regression_target = pd.to_numeric(
        df["actual_delay_days"],
        errors="coerce",
    )

    return (
        classification_target,
        regression_target,
    )


def train_classifier(X_train, y_train):
    """Train a new XGBoost classifier."""

    on_time_count = int(
        (y_train == 0).sum()
    )

    delayed_count = int(
        (y_train == 1).sum()
    )

    scale_pos_weight = (
        on_time_count / delayed_count
        if delayed_count > 0
        else 1.0
    )

    model = XGBClassifier(
        objective="binary:logistic",
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss",
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


def train_regressor(X_train, y_train):
    """Train a new XGBoost regression model."""

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


def evaluate_classifier(model, X_test, y_test):
    """Evaluate the retrained classifier."""

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = {
        "accuracy": round(
            float(
                accuracy_score(
                    y_test,
                    predictions,
                )
            ),
            4,
        ),
        "precision": round(
            float(
                precision_score(
                    y_test,
                    predictions,
                    zero_division=0,
                )
            ),
            4,
        ),
        "recall": round(
            float(
                recall_score(
                    y_test,
                    predictions,
                    zero_division=0,
                )
            ),
            4,
        ),
        "f1": round(
            float(
                f1_score(
                    y_test,
                    predictions,
                    zero_division=0,
                )
            ),
            4,
        ),
    }

    return metrics


def evaluate_regressor(model, X_test, y_test):
    """Evaluate the retrained regression model."""

    predictions = model.predict(
        X_test
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    metrics = {
        "mae_days": round(
            float(
                mean_absolute_error(
                    y_test,
                    predictions,
                )
            ),
            4,
        ),
        "rmse_days": round(
            float(rmse),
            4,
        ),
        "r2": round(
            float(
                r2_score(
                    y_test,
                    predictions,
                )
            ),
            4,
        ),
    }

    return metrics


def save_model_artifacts(
    classifier,
    regressor,
):
    """Save retrained XGBoost models."""

    CLASSIFIER_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    classifier.save_model(
        str(CLASSIFIER_FILE)
    )

    regressor.save_model(
        str(REGRESSOR_FILE)
    )


def build_report(
    trigger,
    df,
    classifier_metrics=None,
    regressor_metrics=None,
    retrained=False,
):
    """Build the retraining report."""

    return {
        "system": "SupplyPrescript",
        "module": "Model Retraining Engine",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "retraining_requested": bool(
            trigger.get(
                "decision",
                {}
            ).get(
                "retraining_required",
                False,
            )
        ),
        "retraining_executed": retrained,
        "training_records": len(df),
        "feature_count": len(
            FEATURE_COLUMNS
        ),
        "classifier_metrics": (
            classifier_metrics
        ),
        "regressor_metrics": (
            regressor_metrics
        ),
        "model_artifacts": {
            "classifier": str(
                CLASSIFIER_FILE
            ),
            "regressor": str(
                REGRESSOR_FILE
            ),
        },
        "next_action": (
            "Continue monitoring the retrained models."
            if retrained
            else
            "Continue using the current models and "
            "collect additional shipment outcomes."
        ),
    }


def save_report(report):
    """Save retraining report."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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


def run_retraining():
    """Run the safe model retraining workflow."""

    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - MODEL RETRAINING ENGINE"
    )
    print("=" * 100)

    print("\nLoading retraining trigger...")

    trigger = load_json(
        TRIGGER_FILE
    )

    decision = trigger.get(
        "decision",
        {}
    )

    retraining_required = bool(
        decision.get(
            "retraining_required",
            False,
        )
    )

    print(
        f"   ✓ Retraining required: "
        f"{retraining_required}"
    )

    print("\nLoading ML feature dataset...")

    df = load_training_data()

    print(
        f"   ✓ Training records available: "
        f"{len(df)}"
    )

    if not retraining_required:
        print(
            "\nRETRAINING SKIPPED"
        )
        print("=" * 100)
        print(
            "The monitoring engine has not requested "
            "model retraining."
        )

        report = build_report(
            trigger=trigger,
            df=df,
            retrained=False,
        )

        save_report(
            report
        )

        print(
            f"\n✓ Retraining report saved:\n"
            f"  {OUTPUT_FILE}"
        )

        print("\n" + "=" * 100)
        print(
            "MODEL RETRAINING ENGINE COMPLETED"
        )
        print("=" * 100)

        return report

    print(
        "\nRetraining condition detected."
    )

    classification_target, regression_target = (
        prepare_targets(df)
    )

    valid_rows = regression_target.notna()

    df = df.loc[
        valid_rows
    ].copy()

    classification_target = (
        classification_target.loc[
            valid_rows
        ]
    )

    regression_target = (
        regression_target.loc[
            valid_rows
        ]
    )

    X = df[
        FEATURE_COLUMNS
    ]

    X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = (
        train_test_split(
            X,
            classification_target,
            regression_target,
            test_size=0.20,
            random_state=42,
            stratify=classification_target,
        )
    )

    print(
        f"   ✓ Training split: {len(X_train)}"
    )

    print(
        f"   ✓ Testing split: {len(X_test)}"
    )

    print(
        "\nTraining XGBoost classifier..."
    )

    classifier = train_classifier(
        X_train,
        y_class_train,
    )

    print(
        "   ✓ Classifier retrained."
    )

    print(
        "\nTraining XGBoost regressor..."
    )

    regressor = train_regressor(
        X_train,
        y_reg_train,
    )

    print(
        "   ✓ Regressor retrained."
    )

    classifier_metrics = evaluate_classifier(
        classifier,
        X_test,
        y_class_test,
    )

    regressor_metrics = evaluate_regressor(
        regressor,
        X_test,
        y_reg_test,
    )

    print(
        "\nRETRAINED MODEL EVALUATION"
    )
    print("=" * 100)

    print(
        f"Classifier accuracy : "
        f"{classifier_metrics['accuracy']:.4f}"
    )

    print(
        f"Classifier F1       : "
        f"{classifier_metrics['f1']:.4f}"
    )

    print(
        f"Regression MAE      : "
        f"{regressor_metrics['mae_days']:.4f} days"
    )

    print(
        f"Regression RMSE     : "
        f"{regressor_metrics['rmse_days']:.4f} days"
    )

    print(
        f"Regression R²       : "
        f"{regressor_metrics['r2']:.4f}"
    )

    save_model_artifacts(
        classifier,
        regressor,
    )

    print(
        "\n✓ Retrained model artifacts saved."
    )

    report = build_report(
        trigger=trigger,
        df=df,
        classifier_metrics=classifier_metrics,
        regressor_metrics=regressor_metrics,
        retrained=True,
    )

    save_report(
        report
    )

    print(
        f"\n✓ Retraining report saved:\n"
        f"  {OUTPUT_FILE}"
    )

    print("\n" + "=" * 100)
    print(
        "MODEL RETRAINING ENGINE COMPLETED"
    )
    print("=" * 100)

    return report


if __name__ == "__main__":
    run_retraining()
