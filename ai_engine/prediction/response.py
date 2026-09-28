import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path.cwd()

INPUT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "ai_intelligence_results.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "ai_response.json"
)


def load_intelligence_results():
    print("Loading AI intelligence results...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"AI intelligence results not found:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    print("   ✓ AI intelligence results loaded.")

    return data


def get_value(data, keys, default=None):
    """
    Finds a value from the supplied keys.

    Supports both:
    1. Top-level AI intelligence fields.
    2. Nested dictionaries used by different AI modules.
    """

    if not isinstance(data, dict):
        return default

    for key in keys:
        if key in data:
            return data[key]

    for value in data.values():
        if isinstance(value, dict):
            result = get_value(value, keys, None)

            if result is not None:
                return result

    return default


def normalize_prediction(value):
    if isinstance(value, dict):
        return value.get(
            "status",
            value.get(
                "prediction",
                value.get("label")
            )
        )

    return value


def normalize_risk_level(data):
    return get_value(
        data,
        [
            "risk_level",
            "riskLevel",
            "risk"
        ],
        None
    )


def normalize_confidence(data):
    confidence = get_value(
        data,
        [
            "confidence"
        ],
        None
    )

    if isinstance(confidence, dict):
        return {
            "score": confidence.get(
                "score",
                confidence.get("confidence")
            ),
            "level": confidence.get(
                "level",
                confidence.get("confidence_level")
            )
        }

    return {
        "score": confidence,
        "level": get_value(
            data,
            [
                "confidence_level"
            ],
            None
        )
    }


def normalize_intelligence(data):
    intelligence = get_value(
        data,
        [
            "intelligence"
        ],
        None
    )

    if isinstance(intelligence, dict):
        return {
            "score": intelligence.get(
                "score",
                intelligence.get("intelligence_score")
            ),
            "level": intelligence.get(
                "level",
                intelligence.get("intelligence_level")
            )
        }

    return {
        "score": intelligence,
        "level": get_value(
            data,
            [
                "intelligence_level"
            ],
            None
        )
    }


def normalize_risk_exposure(data):
    return get_value(
        data,
        [
            "risk_exposure",
            "riskExposure",
            "exposure"
        ],
        None
    )


def normalize_delay_probability(data):
    return get_value(
        data,
        [
            "delay_probability",
            "delayProbability",
            "probability"
        ],
        None
    )


def normalize_expected_delay(data):
    return get_value(
        data,
        [
            "expected_delay_days",
            "expectedDelayDays",
            "delay_days",
            "predicted_delay_days"
        ],
        None
    )


def normalize_risk_drivers(data):
    value = get_value(
        data,
        [
            "risk_drivers"
        ],
        []
    )

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def normalize_historical_evidence(data):
    value = get_value(
        data,
        [
            "historical_evidence"
        ],
        []
    )

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def build_response(data):
    prediction_raw = get_value(
        data,
        [
            "prediction",
            "prediction_status",
            "status"
        ],
        None
    )

    prediction_status = normalize_prediction(
        prediction_raw
    )

    delay_probability = normalize_delay_probability(
        data
    )

    expected_delay_days = normalize_expected_delay(
        data
    )

    risk_level = normalize_risk_level(
        data
    )

    risk_exposure = normalize_risk_exposure(
        data
    )

    confidence = normalize_confidence(
        data
    )

    intelligence = normalize_intelligence(
        data
    )

    risk_drivers = normalize_risk_drivers(
        data
    )

    historical_evidence = normalize_historical_evidence(
        data
    )

    response = {
        "system": "SupplyPrescript",
        "module": "AI Response Engine",
        "engine_version": "1.1",
        "status": "COMPLETED",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "response": {
            "prediction": {
                "status": prediction_status,
                "delay_probability": delay_probability,
                "expected_delay_days": expected_delay_days
            },

            "risk": {
                "level": risk_level,
                "exposure": risk_exposure
            },

            "confidence": {
                "score": confidence["score"],
                "level": confidence["level"]
            },

            "intelligence": {
                "score": intelligence["score"],
                "level": intelligence["level"]
            },

            "risk_drivers": risk_drivers,

            "historical_evidence": historical_evidence
        },

        "response_metadata": {
            "source": "AI Intelligence Engine",
            "machine_readable": True,
            "downstream_ready": True
        },

        "operational_safety": {
            "prediction_modified": False,
            "risk_modified": False,
            "confidence_modified": False,
            "intelligence_modified": False,
            "model_modified": False,
            "recommendation_modified": False,
            "shipment_modified": False,
            "database_modified": False,
            "business_decision_executed": False
        }
    }

    return response


def save_response(response):
    print()
    print("Saving AI response...")

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            response,
            file,
            indent=4
        )

    print("   ✓ AI response saved.")


def print_response(response):
    result = response["response"]

    prediction = result["prediction"]
    risk = result["risk"]
    confidence = result["confidence"]
    intelligence = result["intelligence"]

    print()
    print("=" * 90)
    print("AI RESPONSE")
    print("-" * 90)

    print(
        f"Prediction Status: "
        f"{prediction['status']}"
    )

    print(
        f"Delay Probability: "
        f"{prediction['delay_probability']}"
    )

    print(
        f"Expected Delay: "
        f"{prediction['expected_delay_days']} days"
    )

    print()
    print("RISK")
    print("-" * 90)

    print(
        f"Risk Level: "
        f"{risk['level']}"
    )

    print(
        f"Risk Exposure: "
        f"{risk['exposure']}"
    )

    print()
    print("CONFIDENCE")
    print("-" * 90)

    print(
        f"Confidence Score: "
        f"{confidence['score']}"
    )

    print(
        f"Confidence Level: "
        f"{confidence['level']}"
    )

    print()
    print("AI INTELLIGENCE")
    print("-" * 90)

    print(
        f"Intelligence Score: "
        f"{intelligence['score']}"
    )

    print(
        f"Intelligence Level: "
        f"{intelligence['level']}"
    )

    print()
    print("EXPLAINABILITY")
    print("-" * 90)

    print(
        f"Risk Drivers: "
        f"{len(result['risk_drivers'])}"
    )

    print(
        f"Historical Evidence: "
        f"{len(result['historical_evidence'])}"
    )

    print()
    print("DOWNSTREAM READINESS")
    print("-" * 90)

    print("Machine Readable: YES")
    print("Downstream Ready: YES")

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)

    print("Prediction Modified: NO")
    print("Risk Modified: NO")
    print("Model Modified: NO")
    print("Recommendation Modified: NO")
    print("Shipment Modified: NO")
    print("Database Modified: NO")
    print("Business Decision Executed: NO")


def main():
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI RESPONSE ENGINE"
    )
    print("=" * 90)

    try:
        intelligence = load_intelligence_results()

        print()
        print(
            "Building machine-readable AI response..."
        )

        response = build_response(
            intelligence
        )

        print(
            "   ✓ AI response generated."
        )

        print_response(response)

        save_response(response)

        print()
        print("=" * 90)
        print(
            "AI RESPONSE ENGINE COMPLETED"
        )
        print("=" * 90)
        print(
            f"Response saved: {OUTPUT_FILE}"
        )
        print("=" * 90)

    except Exception as error:
        print()
        print(
            "✗ AI Response Engine failed."
        )
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()