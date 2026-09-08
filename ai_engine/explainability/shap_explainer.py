import json
from pathlib import Path

import pandas as pd
import shap
import xgboost as xgb

PROJECT_ROOT = Path.cwd()

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

FEATURE_DESCRIPTIONS = {
    "distance_km": "Long transportation distance",
    "lead_time_days": "Long lead time",
    "inventory_level": "Low inventory level",
    "supplier_reliability": "Low supplier reliability",
    "order_value": "High order value",
    "fuel_price_index": "High fuel price",
    "warehouse_load": "High warehouse load",
    "supplier_risk": "High supplier risk",
    "weather_risk": "Severe weather conditions",
    "traffic_risk": "High traffic conditions",
    "inventory_risk": "Low inventory risk",
    "warehouse_risk": "High warehouse load risk",
    "distance_risk": "Long-distance transportation risk",
    "transport_risk": "Transport disruption risk",
    "priority_risk": "High shipment priority",
    "fuel_pressure": "High fuel price pressure",
    "lead_time_pressure": "High lead-time pressure",
    "overall_risk_score": "High overall risk score",
}


def load_model():
    model_path = (
        PROJECT_ROOT
        / "ai_engine"
        / "models"
        / "classifier.json"
    )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Classifier model not found: {model_path}"
        )

    model = xgb.XGBClassifier()
    model.load_model(str(model_path))

    return model


def load_feature_data():
    input_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "ml_features.csv"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {input_file}"
        )

    df = pd.read_csv(input_file)

    if df.empty:
        raise ValueError(
            "Feature dataset contains no records."
        )

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing required features: "
            + ", ".join(missing_features)
        )

    return df


def calculate_shap_values(model, X):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    if hasattr(shap_values, "values"):
        shap_values = shap_values.values

    return shap_values


def get_top_shap_drivers(
    row,
    shap_row,
    top_n=4
):
    contributions = []

    for feature, value in zip(
        FEATURE_COLUMNS,
        shap_row
    ):
        contribution = float(value)

        if contribution <= 0:
            continue

        contributions.append(
            {
                "feature": feature,
                "description": FEATURE_DESCRIPTIONS.get(
                    feature,
                    feature
                ),
                "shap_value": contribution,
                "feature_value": float(
                    row[feature]
                ),
            }
        )

    contributions.sort(
        key=lambda item: item["shap_value"],
        reverse=True
    )

    return contributions[:top_n]


def explain_shipments(
    df,
    model,
    limit=10,
    top_n=4
):
    sample = df.head(limit).copy()

    X = sample[FEATURE_COLUMNS]

    shap_values = calculate_shap_values(
        model,
        X
    )

    explanations = []

    for index in range(len(sample)):
        drivers = get_top_shap_drivers(
            sample.iloc[index],
            shap_values[index],
            top_n
        )

        probability = float(
            model.predict_proba(
                X.iloc[[index]]
            )[0][1]
        )

        explanations.append(
            {
                "shipment_id": sample.iloc[index][
                    "shipment_id"
                ],
                "delay_probability": probability,
                "risk_drivers": drivers,
            }
        )

    return explanations


def print_explainability_report(
    explanations
):
    print()
    print(
        "SHAP MODEL EXPLAINABILITY ANALYSIS"
    )
    print("=" * 100)

    for explanation in explanations:
        print()
        print(
            f"Shipment: "
            f"{explanation['shipment_id']}"
        )

        print(
            f"Delay Probability: "
            f"{explanation['delay_probability']:.2%}"
        )

        print("Top SHAP Risk Drivers:")

        drivers = explanation[
            "risk_drivers"
        ]

        if not drivers:
            print(
                "  - No positive risk contributors detected."
            )
            continue

        for index, driver in enumerate(
            drivers,
            start=1
        ):
            print(
                f"  {index}. "
                f"{driver['description']} "
                f"(SHAP: "
                f"{driver['shap_value']:+.4f})"
            )

    print()
    print("=" * 100)


def save_explanations(
    explanations,
    output_file
):
    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            explanations,
            file,
            indent=4
        )

    print(
        f"SHAP explanations saved to: "
        f"{output_path}"
    )


def main():
    print("=" * 100)
    print("SUPPLY PRESCRIPT - SHAP EXPLAINABILITY ENGINE")
    print("=" * 100)

    model = load_model()

    df = load_feature_data()

    explanations = explain_shipments(
        df,
        model,
        limit=10,
        top_n=4
    )

    print_explainability_report(
        explanations
    )

    output_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "explainability"
        / "shap_explanations.json"
    )

    save_explanations(
        explanations,
        output_file
    )

    print()
    print("=" * 100)
    print("SHAP EXPLAINABILITY ENGINE COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()
