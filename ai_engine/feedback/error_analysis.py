from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path.cwd()

FEEDBACK_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "prediction_outcomes.json"
)

SHIPMENT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "data"
    / "raw"
    / "shipments.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "error_analysis.json"
)


def load_feedback():
    """Load prediction-vs-actual feedback."""

    if not FEEDBACK_FILE.exists():
        raise FileNotFoundError(
            f"Feedback file not found: {FEEDBACK_FILE}"
        )

    with open(
        FEEDBACK_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_shipment_data():
    """Load shipment context data."""

    if not SHIPMENT_FILE.exists():
        raise FileNotFoundError(
            f"Shipment dataset not found: {SHIPMENT_FILE}"
        )

    return pd.read_csv(SHIPMENT_FILE)


def get_error_type(record):
    """Classify the prediction outcome."""

    prediction = record.get("prediction", {})
    actual = record.get("actual", {})
    evaluation = record.get("evaluation", {})

    predicted_status = prediction.get(
        "status",
        "UNKNOWN",
    )

    actual_status = actual.get(
        "status",
        "UNKNOWN",
    )

    classification_correct = evaluation.get(
        "classification_correct"
    )

    if classification_correct is True:
        return "CORRECT"

    if (
        predicted_status == "ON_TIME"
        and actual_status == "DELAYED"
    ):
        return "MISSED_DELAY"

    if (
        predicted_status == "DELAYED"
        and actual_status == "ON_TIME"
    ):
        return "FALSE_DELAY_ALERT"

    return "OTHER"


def calculate_error_statistics(records):
    """Calculate overall prediction error statistics."""

    total = len(records)

    if total == 0:
        return {
            "total_evaluated": 0,
            "correct_predictions": 0,
            "incorrect_predictions": 0,
            "classification_accuracy_percent": 0.0,
            "missed_delays": 0,
            "false_delay_alerts": 0,
            "mean_absolute_delay_error_days": 0.0,
            "maximum_absolute_delay_error_days": 0.0,
        }

    correct_predictions = sum(
        1
        for record in records
        if record.get("evaluation", {}).get(
            "classification_correct"
        )
        is True
    )

    missed_delays = sum(
        1
        for record in records
        if get_error_type(record)
        == "MISSED_DELAY"
    )

    false_delay_alerts = sum(
        1
        for record in records
        if get_error_type(record)
        == "FALSE_DELAY_ALERT"
    )

    errors = []

    for record in records:
        error = record.get(
            "evaluation",
            {},
        ).get(
            "absolute_delay_error_days"
        )

        if error is not None:
            errors.append(
                float(error)
            )

    return {
        "total_evaluated": total,
        "correct_predictions": correct_predictions,
        "incorrect_predictions": (
            total - correct_predictions
        ),
        "classification_accuracy_percent": round(
            (correct_predictions / total) * 100,
            2,
        ),
        "missed_delays": missed_delays,
        "false_delay_alerts": false_delay_alerts,
        "mean_absolute_delay_error_days": round(
            sum(errors) / len(errors)
            if errors
            else 0.0,
            4,
        ),
        "maximum_absolute_delay_error_days": round(
            max(errors)
            if errors
            else 0.0,
            4,
        ),
    }


def build_detailed_records(
    records,
    shipment_df,
):
    """Combine feedback with shipment context."""

    shipment_lookup = shipment_df.set_index(
        "shipment_id"
    )

    detailed_records = []

    for record in records:
        shipment_id = record.get(
            "shipment_id"
        )

        prediction = record.get(
            "prediction",
            {}
        )

        actual = record.get(
            "actual",
            {}
        )

        evaluation = record.get(
            "evaluation",
            {}
        )

        detailed_record = {
            "shipment_id": shipment_id,
            "error_type": get_error_type(
                record
            ),
            "predicted_status": prediction.get(
                "status",
                "UNKNOWN",
            ),
            "actual_status": actual.get(
                "status",
                "UNKNOWN",
            ),
            "predicted_delay_days": prediction.get(
                "delay_days"
            ),
            "actual_delay_days": actual.get(
                "delay_days"
            ),
            "classification_correct": evaluation.get(
                "classification_correct"
            ),
            "absolute_delay_error_days": evaluation.get(
                "absolute_delay_error_days"
            ),
        }

        if shipment_id in shipment_lookup.index:
            shipment = shipment_lookup.loc[
                shipment_id
            ]

            detailed_record.update(
                {
                    "transport_mode": str(
                        shipment.get(
                            "transport_mode",
                            "UNKNOWN",
                        )
                    ),
                    "weather_severity": str(
                        shipment.get(
                            "weather_severity",
                            "UNKNOWN",
                        )
                    ),
                    "traffic_level": str(
                        shipment.get(
                            "traffic_level",
                            "UNKNOWN",
                        )
                    ),
                    "priority": str(
                        shipment.get(
                            "priority",
                            "UNKNOWN",
                        )
                    ),
                    "supplier_reliability": float(
                        shipment.get(
                            "supplier_reliability",
                            0,
                        )
                    ),
                    "warehouse_load": float(
                        shipment.get(
                            "warehouse_load",
                            0,
                        )
                    ),
                }
            )

        detailed_records.append(
            detailed_record
        )

    return detailed_records


def calculate_group_analysis(
    detailed_records,
    group_column,
):
    """Calculate prediction errors by category."""

    dataframe = pd.DataFrame(
        detailed_records
    )

    if dataframe.empty:
        return {}

    if group_column not in dataframe.columns:
        return {}

    results = {}

    for group_value, group_df in dataframe.groupby(
        group_column
    ):
        total = len(group_df)

        correct = int(
            group_df[
                "classification_correct"
            ]
            .fillna(False)
            .sum()
        )

        errors = pd.to_numeric(
            group_df[
                "absolute_delay_error_days"
            ],
            errors="coerce",
        ).dropna()

        results[str(group_value)] = {
            "records": total,
            "correct_predictions": correct,
            "incorrect_predictions": (
                total - correct
            ),
            "accuracy_percent": round(
                (correct / total) * 100
                if total
                else 0.0,
                2,
            ),
            "average_delay_error_days": round(
                float(errors.mean())
                if not errors.empty
                else 0.0,
                4,
            ),
            "missed_delays": int(
                (
                    group_df["error_type"]
                    == "MISSED_DELAY"
                ).sum()
            ),
            "false_delay_alerts": int(
                (
                    group_df["error_type"]
                    == "FALSE_DELAY_ALERT"
                ).sum()
            ),
        }

    return results


def generate_recommendations(
    statistics
):
    """Generate model improvement recommendations."""

    recommendations = []

    accuracy = statistics[
        "classification_accuracy_percent"
    ]

    average_error = statistics[
        "mean_absolute_delay_error_days"
    ]

    missed_delays = statistics[
        "missed_delays"
    ]

    false_alerts = statistics[
        "false_delay_alerts"
    ]

    if accuracy < 70:
        recommendations.append(
            "Classification accuracy is below 70%; "
            "additional training data and model "
            "retraining should be considered."
        )
    elif accuracy < 85:
        recommendations.append(
            "Classification performance is acceptable "
            "but should continue to be monitored."
        )
    else:
        recommendations.append(
            "Classification performance is strong "
            "for the current evaluation sample."
        )

    if average_error > 2:
        recommendations.append(
            "Delay-duration error is relatively high; "
            "investigate regression features and "
            "collect additional historical outcomes."
        )
    else:
        recommendations.append(
            "Delay-duration error is within an acceptable "
            "range for the current evaluation sample."
        )

    if missed_delays > 0:
        recommendations.append(
            f"{missed_delays} delayed shipment(s) were "
            "missed by the classifier; investigate "
            "false-negative cases."
        )

    if false_alerts > 0:
        recommendations.append(
            f"{false_alerts} false delay alert(s) were "
            "identified; investigate false-positive cases."
        )

    recommendations.append(
        "Continue collecting actual shipment outcomes "
        "to support future model monitoring and "
        "retraining."
    )

    return recommendations


def save_analysis(analysis):
    """Save the error analysis report."""

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
            analysis,
            file,
            indent=4,
        )


def run_error_analysis():
    """Run the complete AI error analysis engine."""

    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI ERROR ANALYSIS ENGINE"
    )
    print("=" * 100)

    print("\nLoading prediction feedback...")

    feedback = load_feedback()

    records = feedback.get(
        "evaluated_predictions",
        []
    )

    print(
        f"   ✓ Feedback records loaded: "
        f"{len(records)}"
    )

    print("\nLoading shipment context...")

    shipment_df = load_shipment_data()

    print(
        f"   ✓ Shipment records loaded: "
        f"{len(shipment_df)}"
    )

    print("\nAnalyzing prediction errors...")

    statistics = calculate_error_statistics(
        records
    )

    detailed_records = build_detailed_records(
        records,
        shipment_df,
    )

    error_breakdown = {
        "correct": statistics[
            "correct_predictions"
        ],
        "missed_delays": statistics[
            "missed_delays"
        ],
        "false_delay_alerts": statistics[
            "false_delay_alerts"
        ],
        "other": sum(
            1
            for record in detailed_records
            if record["error_type"] == "OTHER"
        ),
    }

    analysis = {
        "system": "SupplyPrescript",
        "module": "AI Error Analysis Engine",
        "overall_statistics": statistics,
        "error_breakdown": error_breakdown,
        "error_by_transport_mode": (
            calculate_group_analysis(
                detailed_records,
                "transport_mode",
            )
        ),
        "error_by_weather": (
            calculate_group_analysis(
                detailed_records,
                "weather_severity",
            )
        ),
        "error_by_traffic": (
            calculate_group_analysis(
                detailed_records,
                "traffic_level",
            )
        ),
        "error_by_priority": (
            calculate_group_analysis(
                detailed_records,
                "priority",
            )
        ),
        "recommendations": generate_recommendations(
            statistics
        ),
        "detailed_records": detailed_records,
    }

    save_analysis(analysis)

    print("\nERROR ANALYSIS SUMMARY")
    print("=" * 100)

    print(
        f"Total evaluated             : "
        f"{statistics['total_evaluated']}"
    )

    print(
        f"Correct predictions         : "
        f"{statistics['correct_predictions']}"
    )

    print(
        f"Incorrect predictions       : "
        f"{statistics['incorrect_predictions']}"
    )

    print(
        f"Classification accuracy     : "
        f"{statistics['classification_accuracy_percent']:.2f}%"
    )

    print(
        f"Missed delays               : "
        f"{statistics['missed_delays']}"
    )

    print(
        f"False delay alerts          : "
        f"{statistics['false_delay_alerts']}"
    )

    print(
        f"Average delay error         : "
        f"{statistics['mean_absolute_delay_error_days']:.2f} days"
    )

    print(
        f"Maximum delay error         : "
        f"{statistics['maximum_absolute_delay_error_days']:.2f} days"
    )

    print("\nRecommendations:")

    for recommendation in analysis[
        "recommendations"
    ]:
        print(
            f"   • {recommendation}"
        )

    print(
        f"\n✓ Error analysis saved:\n"
        f"  {OUTPUT_FILE}"
    )

    print("\n" + "=" * 100)
    print(
        "AI ERROR ANALYSIS ENGINE COMPLETED"
    )
    print("=" * 100)

    return analysis


if __name__ == "__main__":
    run_error_analysis()
