"""
SupplyPrescript - AI Prediction Response Validator

Validates the output produced by the Unified AI Intelligence Engine.

The validator checks the actual nested prediction response structure:

[
    {
        "shipment_id": "...",
        "prediction": {
            "delay_probability": 0.0,
            "prediction": "ON_TIME",
            "expected_delay_days": 0.0,
            "risk_level": "LOW"
        },
        "confidence": {
            "score": 0.0,
            "level": "LOW"
        },
        "intelligence": {
            "score": 0.0,
            "level": "MEDIUM"
        },
        "risk_drivers": [],
        "shap_explanation": [],
        "historical_evidence": {
            "similar_shipments": 0,
            "delayed_shipments": 0,
            "on_time_shipments": 0,
            "historical_delay_rate": 0.0,
            "average_historical_delay_days": 0.0
        }
    }
]

This module is read-only.
It does not modify predictions, models, or optimization decisions.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PREDICTION_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "prediction"
    / "ai_intelligence_results.json"
)

VALID_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}

VALID_PREDICTIONS = {
    "ON_TIME",
    "DELAYED",
}

VALID_CONFIDENCE_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
}

VALID_INTELLIGENCE_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


class PredictionResponseValidator:
    """Validate Unified AI Intelligence Engine responses."""

    def __init__(self) -> None:
        self.checks: List[Dict[str, Any]] = []

    def _add_check(
        self,
        name: str,
        passed: bool,
        message: str,
    ) -> None:
        self.checks.append(
            {
                "check": name,
                "status": "PASS" if passed else "FAIL",
                "message": message,
            }
        )

    def validate_shipment_id(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        shipment_id = prediction.get("shipment_id")

        passed = (
            isinstance(shipment_id, str)
            and bool(shipment_id.strip())
        )

        self._add_check(
            "SHIPMENT_ID",
            passed,
            (
                "Shipment ID is present and valid."
                if passed
                else "Shipment ID is missing or invalid."
            ),
        )

        return passed

    def validate_prediction_object(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        prediction_object = prediction.get("prediction")

        passed = isinstance(
            prediction_object,
            dict,
        )

        self._add_check(
            "PREDICTION_OBJECT",
            passed,
            (
                "Prediction object is present."
                if passed
                else "Prediction object is missing or invalid."
            ),
        )

        return passed

    def validate_delay_probability(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        prediction_object = prediction.get(
            "prediction",
            {},
        )

        if not isinstance(prediction_object, dict):
            self._add_check(
                "DELAY_PROBABILITY",
                False,
                "Prediction object is unavailable.",
            )
            return False

        value = prediction_object.get(
            "delay_probability"
        )

        passed = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and 0.0 <= float(value) <= 1.0
        )

        self._add_check(
            "DELAY_PROBABILITY",
            passed,
            (
                "Delay probability is within the valid range 0 to 1."
                if passed
                else (
                    "Delay probability must be a numeric "
                    "value between 0 and 1."
                )
            ),
        )

        return passed

    def validate_prediction_status(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        prediction_object = prediction.get(
            "prediction",
            {},
        )

        if not isinstance(prediction_object, dict):
            self._add_check(
                "PREDICTION_STATUS",
                False,
                "Prediction object is unavailable.",
            )
            return False

        value = prediction_object.get(
            "prediction"
        )

        normalized = (
            str(value).strip().upper()
            if value is not None
            else ""
        )

        passed = normalized in VALID_PREDICTIONS

        self._add_check(
            "PREDICTION_STATUS",
            passed,
            (
                f"Prediction status '{normalized}' is valid."
                if passed
                else (
                    "Prediction status is invalid. "
                    f"Expected one of: "
                    f"{sorted(VALID_PREDICTIONS)}."
                )
            ),
        )

        return passed

    def validate_expected_delay(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        prediction_object = prediction.get(
            "prediction",
            {},
        )

        if not isinstance(prediction_object, dict):
            self._add_check(
                "EXPECTED_DELAY_DAYS",
                False,
                "Prediction object is unavailable.",
            )
            return False

        value = prediction_object.get(
            "expected_delay_days"
        )

        passed = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and float(value) >= 0.0
        )

        self._add_check(
            "EXPECTED_DELAY_DAYS",
            passed,
            (
                "Expected delay duration is non-negative."
                if passed
                else (
                    "Expected delay duration must be "
                    "a non-negative number."
                )
            ),
        )

        return passed

    def validate_risk_level(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        prediction_object = prediction.get(
            "prediction",
            {},
        )

        if not isinstance(prediction_object, dict):
            self._add_check(
                "RISK_LEVEL",
                False,
                "Prediction object is unavailable.",
            )
            return False

        value = prediction_object.get(
            "risk_level"
        )

        normalized = (
            str(value).strip().upper()
            if value is not None
            else ""
        )

        passed = normalized in VALID_RISK_LEVELS

        self._add_check(
            "RISK_LEVEL",
            passed,
            (
                f"Risk level '{normalized}' is valid."
                if passed
                else (
                    "Risk level is invalid. "
                    f"Expected one of: "
                    f"{sorted(VALID_RISK_LEVELS)}."
                )
            ),
        )

        return passed

    def validate_confidence_object(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        confidence = prediction.get("confidence")

        passed = isinstance(
            confidence,
            dict,
        )

        self._add_check(
            "CONFIDENCE_OBJECT",
            passed,
            (
                "Confidence object is present."
                if passed
                else "Confidence object is missing or invalid."
            ),
        )

        return passed

    def validate_confidence_score(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        confidence = prediction.get(
            "confidence",
            {},
        )

        if not isinstance(confidence, dict):
            self._add_check(
                "CONFIDENCE_SCORE",
                False,
                "Confidence object is unavailable.",
            )
            return False

        value = confidence.get("score")

        passed = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and 0.0 <= float(value) <= 1.0
        )

        self._add_check(
            "CONFIDENCE_SCORE",
            passed,
            (
                "Confidence score is within the valid range 0 to 1."
                if passed
                else (
                    "Confidence score must be a numeric "
                    "value between 0 and 1."
                )
            ),
        )

        return passed

    def validate_confidence_level(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        confidence = prediction.get(
            "confidence",
            {},
        )

        if not isinstance(confidence, dict):
            self._add_check(
                "CONFIDENCE_LEVEL",
                False,
                "Confidence object is unavailable.",
            )
            return False

        value = confidence.get("level")

        normalized = (
            str(value).strip().upper()
            if value is not None
            else ""
        )

        passed = normalized in VALID_CONFIDENCE_LEVELS

        self._add_check(
            "CONFIDENCE_LEVEL",
            passed,
            (
                f"Confidence level '{normalized}' is valid."
                if passed
                else (
                    "Confidence level is invalid. "
                    f"Expected one of: "
                    f"{sorted(VALID_CONFIDENCE_LEVELS)}."
                )
            ),
        )

        return passed

    def validate_intelligence_object(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        intelligence = prediction.get(
            "intelligence"
        )

        passed = isinstance(
            intelligence,
            dict,
        )

        self._add_check(
            "INTELLIGENCE_OBJECT",
            passed,
            (
                "Intelligence object is present."
                if passed
                else "Intelligence object is missing or invalid."
            ),
        )

        return passed

    def validate_intelligence_score(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        intelligence = prediction.get(
            "intelligence",
            {},
        )

        if not isinstance(intelligence, dict):
            self._add_check(
                "INTELLIGENCE_SCORE",
                False,
                "Intelligence object is unavailable.",
            )
            return False

        value = intelligence.get("score")

        passed = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and 0.0 <= float(value) <= 1.0
        )

        self._add_check(
            "INTELLIGENCE_SCORE",
            passed,
            (
                "Intelligence score is within the valid range 0 to 1."
                if passed
                else (
                    "Intelligence score must be a numeric "
                    "value between 0 and 1."
                )
            ),
        )

        return passed

    def validate_intelligence_level(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        intelligence = prediction.get(
            "intelligence",
            {},
        )

        if not isinstance(intelligence, dict):
            self._add_check(
                "INTELLIGENCE_LEVEL",
                False,
                "Intelligence object is unavailable.",
            )
            return False

        value = intelligence.get("level")

        normalized = (
            str(value).strip().upper()
            if value is not None
            else ""
        )

        passed = normalized in VALID_INTELLIGENCE_LEVELS

        self._add_check(
            "INTELLIGENCE_LEVEL",
            passed,
            (
                f"Intelligence level '{normalized}' is valid."
                if passed
                else (
                    "Intelligence level is invalid. "
                    f"Expected one of: "
                    f"{sorted(VALID_INTELLIGENCE_LEVELS)}."
                )
            ),
        )

        return passed

    def validate_risk_drivers(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        risk_drivers = prediction.get(
            "risk_drivers"
        )

        passed = (
            isinstance(risk_drivers, list)
            and all(
                isinstance(driver, str)
                and bool(driver.strip())
                for driver in risk_drivers
            )
        )

        self._add_check(
            "RISK_DRIVERS",
            passed,
            (
                "Risk drivers are provided as a valid list."
                if passed
                else (
                    "Risk drivers must be a list "
                    "of non-empty strings."
                )
            ),
        )

        return passed

    def validate_shap_explanation(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        shap_explanation = prediction.get(
            "shap_explanation"
        )

        if not isinstance(shap_explanation, list):
            self._add_check(
                "SHAP_EXPLANATION",
                False,
                "SHAP explanation must be a list.",
            )
            return False

        valid = True

        for item in shap_explanation:
            if not isinstance(item, dict):
                valid = False
                break

            feature = item.get("feature")
            description = item.get("description")
            shap_value = item.get("shap_value")

            if not isinstance(feature, str) or not feature.strip():
                valid = False
                break

            if (
                not isinstance(description, str)
                or not description.strip()
            ):
                valid = False
                break

            if (
                not isinstance(shap_value, (int, float))
                or isinstance(shap_value, bool)
            ):
                valid = False
                break

        self._add_check(
            "SHAP_EXPLANATION",
            valid,
            (
                "SHAP explanation contains valid feature "
                "explanations."
                if valid
                else (
                    "SHAP explanation contains invalid "
                    "feature data."
                )
            ),
        )

        return valid

    def validate_historical_evidence(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        evidence = prediction.get(
            "historical_evidence"
        )

        if not isinstance(evidence, dict):
            self._add_check(
                "HISTORICAL_EVIDENCE",
                False,
                "Historical evidence must be an object.",
            )
            return False

        required_fields = {
            "similar_shipments",
            "delayed_shipments",
            "on_time_shipments",
            "historical_delay_rate",
            "average_historical_delay_days",
        }

        missing_fields = (
            required_fields
            - set(evidence.keys())
        )

        if missing_fields:
            self._add_check(
                "HISTORICAL_EVIDENCE",
                False,
                (
                    "Historical evidence is missing fields: "
                    f"{sorted(missing_fields)}."
                ),
            )
            return False

        integer_fields = {
            "similar_shipments",
            "delayed_shipments",
            "on_time_shipments",
        }

        numeric_fields = {
            "historical_delay_rate",
            "average_historical_delay_days",
        }

        valid = True

        for field in integer_fields:
            value = evidence.get(field)

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or float(value) < 0
                or float(value) != int(value)
            ):
                valid = False
                break

        if valid:
            for field in numeric_fields:
                value = evidence.get(field)

                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or float(value) < 0
                ):
                    valid = False
                    break

        historical_delay_rate = evidence.get(
            "historical_delay_rate"
        )

        if valid and not (
            0.0 <= float(historical_delay_rate) <= 1.0
        ):
            valid = False

        self._add_check(
            "HISTORICAL_EVIDENCE",
            valid,
            (
                "Historical evidence contains valid metrics."
                if valid
                else (
                    "Historical evidence contains "
                    "invalid metric values."
                )
            ),
        )

        return valid

    def validate_cross_field_consistency(
        self,
        prediction: Dict[str, Any],
    ) -> bool:
        prediction_object = prediction.get(
            "prediction",
            {},
        )

        evidence = prediction.get(
            "historical_evidence",
            {},
        )

        if not isinstance(
            prediction_object,
            dict,
        ) or not isinstance(
            evidence,
            dict,
        ):
            self._add_check(
                "CROSS_FIELD_CONSISTENCY",
                False,
                "Required nested objects are unavailable.",
            )
            return False

        delayed_shipments = evidence.get(
            "delayed_shipments"
        )

        similar_shipments = evidence.get(
            "similar_shipments"
        )

        on_time_shipments = evidence.get(
            "on_time_shipments"
        )

        historical_delay_rate = evidence.get(
            "historical_delay_rate"
        )

        valid = True

        if (
            isinstance(delayed_shipments, (int, float))
            and isinstance(similar_shipments, (int, float))
            and delayed_shipments > similar_shipments
        ):
            valid = False

        if (
            isinstance(on_time_shipments, (int, float))
            and isinstance(similar_shipments, (int, float))
            and on_time_shipments > similar_shipments
        ):
            valid = False

        if (
            isinstance(delayed_shipments, (int, float))
            and isinstance(on_time_shipments, (int, float))
            and isinstance(similar_shipments, (int, float))
            and (
                delayed_shipments + on_time_shipments
                > similar_shipments
            )
        ):
            valid = False

        if (
            isinstance(
                delayed_shipments,
                (int, float),
            )
            and isinstance(
                similar_shipments,
                (int, float),
            )
            and similar_shipments > 0
        ):
            calculated_rate = (
                delayed_shipments
                / similar_shipments
            )

            if (
                isinstance(
                    historical_delay_rate,
                    (int, float),
                )
                and abs(
                    calculated_rate
                    - float(historical_delay_rate)
                ) > 0.05
            ):
                valid = False

        predicted_status = prediction_object.get(
            "prediction"
        )

        delay_probability = prediction_object.get(
            "delay_probability"
        )

        if (
            predicted_status == "DELAYED"
            and isinstance(delay_probability, (int, float))
            and float(delay_probability) < 0.5
        ):
            valid = False

        if (
            predicted_status == "ON_TIME"
            and isinstance(delay_probability, (int, float))
            and float(delay_probability) >= 0.5
        ):
            valid = False

        self._add_check(
            "CROSS_FIELD_CONSISTENCY",
            valid,
            (
                "Nested prediction and historical metrics "
                "are internally consistent."
                if valid
                else (
                    "Prediction and historical evidence "
                    "contain inconsistent values."
                )
            ),
        )

        return valid

    def validate(
        self,
        prediction: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run all validation checks for one shipment."""

        self.checks = []

        if not isinstance(
            prediction,
            dict,
        ):
            return {
                "validation_status": "INVALID",
                "validation_score": 0.0,
                "total_checks": 1,
                "passed_checks": 0,
                "failed_checks": 1,
                "checks": [
                    {
                        "check": "RESPONSE_TYPE",
                        "status": "FAIL",
                        "message": (
                            "Prediction record must be "
                            "a JSON object."
                        ),
                    }
                ],
            }

        self.validate_shipment_id(
            prediction
        )

        self.validate_prediction_object(
            prediction
        )

        self.validate_delay_probability(
            prediction
        )

        self.validate_prediction_status(
            prediction
        )

        self.validate_expected_delay(
            prediction
        )

        self.validate_risk_level(
            prediction
        )

        self.validate_confidence_object(
            prediction
        )

        self.validate_confidence_score(
            prediction
        )

        self.validate_confidence_level(
            prediction
        )

        self.validate_intelligence_object(
            prediction
        )

        self.validate_intelligence_score(
            prediction
        )

        self.validate_intelligence_level(
            prediction
        )

        self.validate_risk_drivers(
            prediction
        )

        self.validate_shap_explanation(
            prediction
        )

        self.validate_historical_evidence(
            prediction
        )

        self.validate_cross_field_consistency(
            prediction
        )

        passed_checks = sum(
            1
            for check in self.checks
            if check["status"] == "PASS"
        )

        failed_checks = (
            len(self.checks)
            - passed_checks
        )

        total_checks = len(self.checks)

        validation_score = (
            (
                passed_checks
                / total_checks
            )
            * 100
            if total_checks > 0
            else 0.0
        )

        validation_status = (
            "VALID"
            if failed_checks == 0
            else "INVALID"
        )

        return {
            "validation_status": validation_status,
            "validation_score": round(
                validation_score,
                2,
            ),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "checks": self.checks,
        }


def load_prediction_file() -> Any:
    """Load the AI Intelligence Engine prediction file."""

    if not PREDICTION_FILE.exists():
        raise FileNotFoundError(
            f"Prediction file not found: "
            f"{PREDICTION_FILE}"
        )

    with PREDICTION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def validate_all_predictions(
    payload: Any,
) -> Dict[str, Any]:
    """Validate every shipment prediction in the output."""

    if not isinstance(payload, list):
        raise ValueError(
            "AI intelligence output must be a list "
            "of prediction records."
        )

    validator = PredictionResponseValidator()

    shipment_results: List[Dict[str, Any]] = []

    total_shipments = len(payload)
    valid_shipments = 0
    invalid_shipments = 0

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    for prediction in payload:
        result = validator.validate(
            prediction
        )

        shipment_id = (
            prediction.get("shipment_id")
            if isinstance(
                prediction,
                dict,
            )
            else None
        )

        shipment_result = {
            "shipment_id": shipment_id,
            "validation": result,
        }

        shipment_results.append(
            shipment_result
        )

        if (
            result["validation_status"]
            == "VALID"
        ):
            valid_shipments += 1
        else:
            invalid_shipments += 1

        total_checks += result[
            "total_checks"
        ]

        passed_checks += result[
            "passed_checks"
        ]

        failed_checks += result[
            "failed_checks"
        ]

    overall_score = (
        (
            passed_checks
            / total_checks
        )
        * 100
        if total_checks > 0
        else 0.0
    )

    overall_status = (
        "VALID"
        if invalid_shipments == 0
        else "INVALID"
    )

    return {
        "validation_status": overall_status,
        "validation_score": round(
            overall_score,
            2,
        ),
        "total_shipments": total_shipments,
        "valid_shipments": valid_shipments,
        "invalid_shipments": invalid_shipments,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "shipment_results": shipment_results,
    }


def main() -> None:
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - "
        "AI PREDICTION RESPONSE VALIDATOR"
    )
    print("=" * 100)

    print("\nSearching for AI prediction output...")

    try:
        payload = load_prediction_file()

        print(
            "   ✓ Prediction output loaded."
        )

        print(
            f"     {PREDICTION_FILE}"
        )

        print(
            f"\nFound {len(payload)} "
            "prediction records."
        )

        print(
            "\nValidating all AI prediction responses..."
        )

        result = validate_all_predictions(
            payload
        )

        print(
            "\nPREDICTION VALIDATION RESULT"
        )
        print("=" * 100)

        print(
            f"Validation Status: "
            f"{result['validation_status']}"
        )

        print(
            f"Validation Score: "
            f"{result['validation_score']:.2f}%"
        )

        print(
            f"Total Shipments: "
            f"{result['total_shipments']}"
        )

        print(
            f"Valid Shipments: "
            f"{result['valid_shipments']}"
        )

        print(
            f"Invalid Shipments: "
            f"{result['invalid_shipments']}"
        )

        print(
            f"Total Checks: "
            f"{result['total_checks']}"
        )

        print(
            f"Passed Checks: "
            f"{result['passed_checks']}"
        )

        print(
            f"Failed Checks: "
            f"{result['failed_checks']}"
        )

        print(
            "\nShipment Validation Summary:"
        )

        for shipment_result in result[
            "shipment_results"
        ]:
            shipment_id = (
                shipment_result[
                    "shipment_id"
                ]
                or "UNKNOWN"
            )

            validation = shipment_result[
                "validation"
            ]

            print(
                f"   {validation['validation_status']:<7} "
                f"- {shipment_id} "
                f"({validation['validation_score']:.2f}%)"
            )

        print("\nDownstream Safety:")

        if (
            result["validation_status"]
            == "VALID"
        ):
            print(
                "   ✓ All prediction responses "
                "passed validation."
            )

            print(
                "   ✓ AI output is safe for "
                "downstream consumption."
            )

            print(
                "   ✓ Optimization engine can "
                "consume the validated structure."
            )

        else:
            print(
                "   ✗ One or more prediction "
                "responses failed validation."
            )

            print(
                "   ✗ AI output should not be "
                "forwarded to downstream decision systems."
            )

        report = {
            "engine": (
                "AI Prediction Response Validator"
            ),
            "generated_at": datetime.now().isoformat(),
            "prediction_file": str(
                PREDICTION_FILE
            ),
            "validation": result,
            "operational_scope": {
                "prediction_modified": False,
                "model_modified": False,
                "optimization_executed": False,
                "validator_only": True,
            },
        }

        output_file = (
            PROJECT_ROOT
            / "ai_engine"
            / "prediction"
            / "prediction_validation_report.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
            )

        print(
            "\n✓ Validation report saved:"
        )

        print(
            f"  {output_file}"
        )

    except FileNotFoundError as error:
        print(
            f"\n✗ File error: {error}"
        )

    except json.JSONDecodeError as error:
        print(
            "\n✗ Failed to parse AI prediction JSON:"
        )

        print(
            f"  {error}"
        )

    except ValueError as error:
        print(
            f"\n✗ Validation input error: "
            f"{error}"
        )

    except Exception as error:
        print(
            "\n✗ Unexpected validation error:"
        )

        print(
            f"  {error}"
        )


if __name__ == "__main__":
    main()