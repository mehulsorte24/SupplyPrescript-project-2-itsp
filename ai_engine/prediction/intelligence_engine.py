import json
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path.cwd()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ai_engine.prediction.predictor import (
    predict_from_dataset,
)

from ai_engine.prediction.confidence import (
    add_confidence_scores,
)

from ai_engine.explainability.risk_drivers import (
    explain_dataset,
)

from ai_engine.explainability.shap_explainer import (
    load_model,
    explain_shipments,
)

from ai_engine.similarity.historical_similarity import (
    load_feature_data,
    generate_similarity_evidence,
)


INPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "data"
    / "processed"
    / "ml_features.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "ai_intelligence_results.json"
)


def calculate_intelligence_score(
    delay_probability,
    confidence_score,
    historical_delay_rate,
):
    """
    Calculate a unified operational intelligence score.

    This score combines:
    - XGBoost delay probability
    - prediction confidence
    - historical delay evidence

    The result is an operational ranking score,
    not a probability.
    """

    score = (
        0.50 * delay_probability
        + 0.20 * confidence_score
        + 0.30 * historical_delay_rate
    )

    return round(
        min(max(score, 0.0), 1.0),
        4,
    )


def classify_intelligence_level(
    intelligence_score,
):
    """
    Convert the unified intelligence score
    into an operational severity level.
    """

    if intelligence_score >= 0.80:
        return "CRITICAL"

    if intelligence_score >= 0.60:
        return "HIGH"

    if intelligence_score >= 0.40:
        return "MEDIUM"

    return "LOW"


def build_confidence_lookup(
    predictions_with_confidence,
):
    """
    Create a shipment_id based lookup
    for confidence results.
    """

    lookup = {}

    for _, row in predictions_with_confidence.iterrows():
        shipment_id = str(
            row["shipment_id"]
        )

        lookup[shipment_id] = {
            "confidence_score": float(
                row["confidence_score"]
            ),
            "confidence_level": row[
                "confidence_level"
            ],
        }

    return lookup


def build_risk_driver_lookup(
    explained_data,
):
    """
    Create a shipment_id based lookup
    for feature-based risk drivers.
    """

    lookup = {}

    for _, row in explained_data.iterrows():
        shipment_id = str(
            row["shipment_id"]
        )

        drivers = row.get(
            "risk_drivers",
            [],
        )

        lookup[shipment_id] = drivers

    return lookup


def build_shap_lookup(
    shap_explanations,
):
    """
    Create a shipment_id based lookup
    for SHAP explanations.
    """

    lookup = {}

    for explanation in shap_explanations:
        shipment_id = str(
            explanation["shipment_id"]
        )

        lookup[shipment_id] = explanation

    return lookup


def build_similarity_lookup(
    df,
    limit,
    n_neighbors=10,
):
    """
    Generate historical similarity evidence
    for the selected shipments.
    """

    lookup = {}

    sample_size = min(
        limit,
        len(df),
    )

    for shipment_index in range(
        sample_size
    ):
        result = generate_similarity_evidence(
            df,
            shipment_index,
            n_neighbors=n_neighbors,
        )

        shipment_id = str(
            result["shipment_id"]
        )

        lookup[shipment_id] = result

    return lookup


def build_intelligence_record(
    shipment_id,
    prediction,
    confidence,
    risk_drivers,
    shap_explanation,
    similarity_result,
):
    """
    Combine all AI engines into one
    unified intelligence response.
    """

    historical_evidence = similarity_result.get(
        "historical_evidence",
        {},
    )

    delay_probability = float(
        prediction["delay_probability"]
    )

    expected_delay_days = float(
        prediction["expected_delay_days"]
    )

    confidence_score = float(
        confidence["confidence_score"]
    )

    historical_delay_rate = float(
        historical_evidence.get(
            "historical_delay_rate",
            0.0,
        )
    )

    intelligence_score = (
        calculate_intelligence_score(
            delay_probability=delay_probability,
            confidence_score=confidence_score,
            historical_delay_rate=historical_delay_rate,
        )
    )

    intelligence_level = (
        classify_intelligence_level(
            intelligence_score
        )
    )

    shap_drivers = []

    for driver in shap_explanation.get(
        "risk_drivers",
        [],
    ):
        shap_drivers.append(
            {
                "feature": driver.get(
                    "feature"
                ),
                "description": driver.get(
                    "description"
                ),
                "shap_value": round(
                    float(
                        driver.get(
                            "shap_value",
                            0.0,
                        )
                    ),
                    4,
                ),
            }
        )

    return {
        "shipment_id": shipment_id,

        "prediction": {
            "delay_probability": round(
                delay_probability,
                4,
            ),
            "prediction": prediction[
                "prediction"
            ],
            "expected_delay_days": round(
                expected_delay_days,
                2,
            ),
            "risk_level": prediction[
                "risk_level"
            ],
        },

        "confidence": {
            "score": round(
                confidence_score,
                4,
            ),
            "level": confidence[
                "confidence_level"
            ],
        },

        "intelligence": {
            "score": intelligence_score,
            "level": intelligence_level,
        },

        "risk_drivers": risk_drivers,

        "shap_explanation": shap_drivers,

        "historical_evidence": {
            "similar_shipments": int(
                historical_evidence.get(
                    "similar_shipments",
                    0,
                )
            ),
            "delayed_shipments": int(
                historical_evidence.get(
                    "delayed_shipments",
                    0,
                )
            ),
            "on_time_shipments": int(
                historical_evidence.get(
                    "on_time_shipments",
                    0,
                )
            ),
            "historical_delay_rate": round(
                historical_delay_rate,
                4,
            ),
            "average_historical_delay_days": round(
                float(
                    historical_evidence.get(
                        "average_historical_delay_days",
                        0.0,
                    )
                ),
                2,
            ),
        },
    }


def run_intelligence_engine(
    limit=10,
):
    """
    Execute the complete SupplyPrescript
    AI Intelligence Engine.
    """

    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI INTELLIGENCE ENGINE"
    )
    print("=" * 100)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {INPUT_FILE}"
        )

    if limit <= 0:
        raise ValueError(
            "Limit must be greater than zero."
        )

    print()
    print("Loading feature dataset...")

    df = load_feature_data(
        INPUT_FILE
    )

    sample = df.head(limit).copy()

    print(
        f"Total dataset records : {len(df)}"
    )

    print(
        f"Records selected      : {len(sample)}"
    )

    print()

    # ---------------------------------------------------------
    # 1. XGBoost Prediction
    # ---------------------------------------------------------

    print(
        "1. Running XGBoost prediction engine..."
    )

    predictions = predict_from_dataset(
        str(INPUT_FILE),
        limit=limit,
    )

    print(
        f"   ✓ Predictions generated: "
        f"{len(predictions)}"
    )

    # ---------------------------------------------------------
    # 2. Confidence Engine
    # ---------------------------------------------------------

    print(
        "2. Running prediction confidence engine..."
    )

    predictions_with_confidence = (
        add_confidence_scores(
            predictions
        )
    )

    confidence_lookup = (
        build_confidence_lookup(
            predictions_with_confidence
        )
    )

    print(
        f"   ✓ Confidence scores generated: "
        f"{len(confidence_lookup)}"
    )

    # ---------------------------------------------------------
    # 3. Risk Driver Engine
    # ---------------------------------------------------------

    print(
        "3. Running risk-driver explainability..."
    )

    explained_data = explain_dataset(
        str(INPUT_FILE),
        limit=limit,
        top_n=4,
    )

    risk_driver_lookup = (
        build_risk_driver_lookup(
            explained_data
        )
    )

    print(
        f"   ✓ Risk explanations generated: "
        f"{len(risk_driver_lookup)}"
    )

    # ---------------------------------------------------------
    # 4. SHAP Explainability
    # ---------------------------------------------------------

    print(
        "4. Running SHAP model explainability..."
    )

    shap_model = load_model()

    shap_explanations = explain_shipments(
        sample,
        shap_model,
        limit=limit,
        top_n=4,
    )

    shap_lookup = build_shap_lookup(
        shap_explanations
    )

    print(
        f"   ✓ SHAP explanations generated: "
        f"{len(shap_lookup)}"
    )

    # ---------------------------------------------------------
    # 5. Historical Similarity
    # ---------------------------------------------------------

    print(
        "5. Running historical similarity engine..."
    )

    similarity_lookup = (
        build_similarity_lookup(
            df,
            limit=limit,
            n_neighbors=10,
        )
    )

    print(
        f"   ✓ Historical evidence generated: "
        f"{len(similarity_lookup)}"
    )

    # ---------------------------------------------------------
    # 6. Unified Intelligence
    # ---------------------------------------------------------

    print()
    print(
        "6. Building unified AI intelligence..."
    )

    prediction_lookup = {}

    for _, row in predictions_with_confidence.iterrows():

        shipment_id = str(
            row["shipment_id"]
        )

        prediction_lookup[shipment_id] = {
            "delay_probability": float(
                row["delay_probability"]
            ),
            "prediction": row[
                "prediction"
            ],
            "expected_delay_days": float(
                row["expected_delay_days"]
            ),
            "risk_level": row[
                "risk_level"
            ],
        }

    intelligence_results = []

    for shipment_id in prediction_lookup:

        if shipment_id not in confidence_lookup:
            continue

        if shipment_id not in risk_driver_lookup:
            continue

        if shipment_id not in shap_lookup:
            continue

        if shipment_id not in similarity_lookup:
            continue

        record = build_intelligence_record(
            shipment_id=shipment_id,
            prediction=prediction_lookup[
                shipment_id
            ],
            confidence=confidence_lookup[
                shipment_id
            ],
            risk_drivers=risk_driver_lookup[
                shipment_id
            ],
            shap_explanation=shap_lookup[
                shipment_id
            ],
            similarity_result=similarity_lookup[
                shipment_id
            ],
        )

        intelligence_results.append(
            record
        )

    # ---------------------------------------------------------
    # 7. Save Unified Results
    # ---------------------------------------------------------

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
            intelligence_results,
            file,
            indent=4,
        )

    print(
        f"   ✓ Unified records created: "
        f"{len(intelligence_results)}"
    )

    print()
    print(
        f"Output file: {OUTPUT_FILE}"
    )

    # ---------------------------------------------------------
    # 8. Operational Summary
    # ---------------------------------------------------------

    if intelligence_results:

        critical = sum(
            1
            for result in intelligence_results
            if result["intelligence"]["level"]
            == "CRITICAL"
        )

        high = sum(
            1
            for result in intelligence_results
            if result["intelligence"]["level"]
            == "HIGH"
        )

        medium = sum(
            1
            for result in intelligence_results
            if result["intelligence"]["level"]
            == "MEDIUM"
        )

        low = sum(
            1
            for result in intelligence_results
            if result["intelligence"]["level"]
            == "LOW"
        )

        average_probability = (
            sum(
                result["prediction"][
                    "delay_probability"
                ]
                for result in intelligence_results
            )
            / len(intelligence_results)
        )

        average_delay = (
            sum(
                result["prediction"][
                    "expected_delay_days"
                ]
                for result in intelligence_results
            )
            / len(intelligence_results)
        )

        average_confidence = (
            sum(
                result["confidence"]["score"]
                for result in intelligence_results
            )
            / len(intelligence_results)
        )

        print()
        print("=" * 100)
        print(
            "AI INTELLIGENCE SUMMARY"
        )
        print("=" * 100)

        print(
            f"Total intelligence records : "
            f"{len(intelligence_results)}"
        )

        print(
            f"Critical intelligence      : "
            f"{critical}"
        )

        print(
            f"High intelligence          : "
            f"{high}"
        )

        print(
            f"Medium intelligence        : "
            f"{medium}"
        )

        print(
            f"Low intelligence           : "
            f"{low}"
        )

        print(
            f"Average delay probability  : "
            f"{average_probability:.2%}"
        )

        print(
            f"Average expected delay     : "
            f"{average_delay:.2f} days"
        )

        print(
            f"Average confidence         : "
            f"{average_confidence:.2%}"
        )

        print()
        print(
            "SAMPLE UNIFIED INTELLIGENCE"
        )
        print("=" * 100)

        print(
            json.dumps(
                intelligence_results[0],
                indent=4,
            )
        )

    print()
    print("=" * 100)
    print(
        "AI INTELLIGENCE ENGINE COMPLETED"
    )
    print("=" * 100)

    return intelligence_results


def main():
    run_intelligence_engine(
        limit=10
    )


if __name__ == "__main__":
    main()
