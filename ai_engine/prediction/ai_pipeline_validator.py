import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path.cwd()

REPORT_FILE = (
    BASE_DIR
    / "ai_engine"
    / "prediction"
    / "ai_pipeline_validation_report.json"
)


ARTIFACTS = [
    {
        "name": "Shipment Schema",
        "path": "ai_engine/data/schemas/shipment_schema.py",
        "type": "file",
    },
    {
        "name": "Data Validator",
        "path": "ai_engine/data/validation/validator.py",
        "type": "file",
    },
    {
        "name": "Data Cleaner",
        "path": "ai_engine/preprocessing/cleaner.py",
        "type": "file",
    },
    {
        "name": "Preprocessing Pipeline",
        "path": "ai_engine/preprocessing/pipeline.py",
        "type": "file",
    },
    {
        "name": "Feature Pipeline",
        "path": "ai_engine/features/feature_pipeline.py",
        "type": "file",
    },
    {
        "name": "Classifier Training",
        "path": "ai_engine/models/train_classifier.py",
        "type": "file",
    },
    {
        "name": "Regressor Training",
        "path": "ai_engine/models/train_regressor.py",
        "type": "file",
    },
    {
        "name": "Prediction Engine",
        "path": "ai_engine/prediction/predictor.py",
        "type": "file",
    },
    {
        "name": "Confidence Engine",
        "path": "ai_engine/prediction/confidence.py",
        "type": "file",
    },
    {
        "name": "AI Response Engine",
        "path": "ai_engine/prediction/response.py",
        "type": "file",
    },
    {
        "name": "AI Intelligence Engine",
        "path": "ai_engine/prediction/intelligence_engine.py",
        "type": "file",
    },
    {
        "name": "Prediction Response Validator",
        "path": "ai_engine/prediction/response_validator.py",
        "type": "file",
    },
    {
        "name": "Batch Quality Monitor",
        "path": "ai_engine/prediction/batch_quality_monitor.py",
        "type": "file",
    },
    {
        "name": "Batch Quality Trend",
        "path": "ai_engine/prediction/batch_quality_trend.py",
        "type": "file",
    },
    {
        "name": "Batch Quality History",
        "path": "ai_engine/prediction/batch_quality_history.py",
        "type": "file",
    },
    {
        "name": "Batch Risk Aggregation",
        "path": "ai_engine/prediction/batch_risk_aggregation.py",
        "type": "file",
    },
    {
        "name": "Batch Risk Escalation",
        "path": "ai_engine/prediction/batch_risk_escalation.py",
        "type": "file",
    },
    {
        "name": "Escalation History",
        "path": "ai_engine/prediction/escalation_history.py",
        "type": "file",
    },
    {
        "name": "Escalation Pattern Analyzer",
        "path": "ai_engine/prediction/escalation_pattern_analyzer.py",
        "type": "file",
    },
    {
        "name": "Escalation Trend Intelligence",
        "path": "ai_engine/prediction/escalation_trend_intelligence.py",
        "type": "file",
    },
    {
        "name": "Decision Intelligence",
        "path": "ai_engine/prediction/decision_intelligence.py",
        "type": "file",
    },
    {
        "name": "Action Recommendation",
        "path": "ai_engine/prediction/action_recommendation.py",
        "type": "file",
    },
    {
        "name": "Manager Decision",
        "path": "ai_engine/prediction/manager_decision.py",
        "type": "file",
    },
    {
        "name": "Decision Outcome Tracker",
        "path": "ai_engine/feedback/decision_outcome_tracker.py",
        "type": "file",
    },
    {
        "name": "Recommendation Outcome Analyzer",
        "path": "ai_engine/feedback/recommendation_outcome_analyzer.py",
        "type": "file",
    },
    {
        "name": "Recommendation Learning Signal",
        "path": "ai_engine/feedback/recommendation_learning_signal.py",
        "type": "file",
    },
    {
        "name": "Recommendation Learning History",
        "path": "ai_engine/feedback/recommendation_learning_history.py",
        "type": "file",
    },
    {
        "name": "Prediction Feedback Engine",
        "path": "ai_engine/feedback/outcome_tracker.py",
        "type": "file",
    },
    {
        "name": "Error Analysis Engine",
        "path": "ai_engine/feedback/error_analysis.py",
        "type": "file",
    },
    {
        "name": "Model Monitoring Engine",
        "path": "ai_engine/feedback/model_monitor.py",
        "type": "file",
    },
]


GENERATED_OUTPUTS = [
    {
        "name": "AI Intelligence Results",
        "path": "ai_engine/prediction/ai_intelligence_results.json",
    },
    {
        "name": "Prediction Validation Report",
        "path": "ai_engine/prediction/prediction_validation_report.json",
    },
    {
        "name": "Batch Quality Report",
        "path": "ai_engine/prediction/batch_quality_report.json",
    },
    {
        "name": "Batch Risk Aggregation Report",
        "path": "ai_engine/prediction/batch_risk_aggregation_report.json",
    },
    {
        "name": "Batch Risk Escalation Report",
        "path": "ai_engine/prediction/batch_risk_escalation_report.json",
    },
    {
        "name": "Decision Intelligence Report",
        "path": "ai_engine/prediction/decision_intelligence_report.json",
    },
    {
        "name": "Action Recommendation Report",
        "path": "ai_engine/prediction/action_recommendation_report.json",
    },
    {
        "name": "Manager Decision",
        "path": "ai_engine/prediction/manager_decision.json",
    },
    {
        "name": "Decision Outcome",
        "path": "ai_engine/feedback/decision_outcomes.json",
    },
    {
        "name": "Recommendation Outcome Analysis",
        "path": "ai_engine/feedback/recommendation_outcome_analysis.json",
    },
    {
        "name": "Recommendation Learning Signal",
        "path": "ai_engine/feedback/recommendation_learning_signal.json",
    },
    {
        "name": "Recommendation Learning History",
        "path": "ai_engine/feedback/recommendation_learning_history.json",
    },
]


def check_file(relative_path):
    path = BASE_DIR / relative_path
    return path.exists() and path.is_file()


def check_json(relative_path):
    path = BASE_DIR / relative_path

    if not path.exists():
        return False, "FILE_NOT_FOUND"

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if data is None:
            return False, "EMPTY_JSON"

        return True, "VALID_JSON"

    except json.JSONDecodeError:
        return False, "INVALID_JSON"

    except Exception as error:
        return False, str(error)


def validate_artifacts():
    results = []

    for artifact in ARTIFACTS:
        exists = check_file(artifact["path"])

        results.append(
            {
                "name": artifact["name"],
                "path": artifact["path"],
                "available": exists,
                "status": "READY" if exists else "MISSING",
            }
        )

    return results


def validate_outputs():
    results = []

    for output in GENERATED_OUTPUTS:
        valid, status = check_json(output["path"])

        results.append(
            {
                "name": output["name"],
                "path": output["path"],
                "available": valid,
                "status": status,
            }
        )

    return results


def calculate_summary(artifact_results, output_results):
    total_artifacts = len(artifact_results)
    available_artifacts = sum(
        1
        for item in artifact_results
        if item["available"]
    )

    total_outputs = len(output_results)
    available_outputs = sum(
        1
        for item in output_results
        if item["available"]
    )

    total_checks = total_artifacts + total_outputs
    passed_checks = available_artifacts + available_outputs

    if total_checks == 0:
        readiness = 0.0
    else:
        readiness = round(
            (passed_checks / total_checks) * 100,
            2
        )

    if readiness == 100:
        status = "READY"

    elif readiness >= 90:
        status = "MOSTLY_READY"

    elif readiness >= 75:
        status = "PARTIALLY_READY"

    else:
        status = "NOT_READY"

    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": total_checks - passed_checks,
        "readiness_percentage": readiness,
        "status": status,
    }


def build_report():
    print()
    print("Checking AI source modules...")

    artifact_results = validate_artifacts()

    print("   ✓ Source module validation completed.")

    print()
    print("Checking generated AI outputs...")

    output_results = validate_outputs()

    print("   ✓ Generated output validation completed.")

    summary = calculate_summary(
        artifact_results,
        output_results
    )

    return {
        "system": "SupplyPrescript",
        "module": "AI End-to-End Pipeline Validator",
        "engine_version": "1.0",
        "status": "COMPLETED",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "summary": summary,

        "source_modules": artifact_results,

        "generated_outputs": output_results,

        "pipeline_stages": [
            "Data Validation",
            "Data Cleaning",
            "Preprocessing",
            "Feature Engineering",
            "Classification",
            "Regression",
            "Prediction",
            "Confidence Analysis",
            "Explainability",
            "Historical Similarity",
            "AI Intelligence",
            "Prediction Validation",
            "Batch Quality Monitoring",
            "Risk Aggregation",
            "Risk Escalation",
            "Decision Intelligence",
            "Action Recommendation",
            "Manager Decision",
            "Outcome Tracking",
            "Recommendation Outcome Analysis",
            "Learning Signal",
            "Learning History",
            "Feedback Monitoring",
        ],

        "operational_safety": {
            "source_data_modified": False,
            "prediction_outputs_modified": False,
            "model_artifacts_modified": False,
            "recommendation_weights_modified": False,
            "models_retrained": False,
            "manager_decisions_modified": False,
            "shipments_modified": False,
            "database_modified": False,
            "business_decision_executed": False,
        },
    }


def print_report(report):
    summary = report["summary"]

    print()
    print("=" * 90)
    print("AI END-TO-END PIPELINE VALIDATION")
    print("-" * 90)

    print(
        f"Total Checks: {summary['total_checks']}"
    )

    print(
        f"Passed Checks: {summary['passed_checks']}"
    )

    print(
        f"Failed Checks: {summary['failed_checks']}"
    )

    print(
        f"Pipeline Readiness: "
        f"{summary['readiness_percentage']}%"
    )

    print(
        f"Overall Status: {summary['status']}"
    )

    print()
    print("SOURCE MODULES")
    print("-" * 90)

    for item in report["source_modules"]:
        symbol = "✓" if item["available"] else "✗"

        print(
            f"{symbol} "
            f"{item['name']} - "
            f"{item['status']}"
        )

    print()
    print("GENERATED OUTPUTS")
    print("-" * 90)

    for item in report["generated_outputs"]:
        symbol = "✓" if item["available"] else "✗"

        print(
            f"{symbol} "
            f"{item['name']} - "
            f"{item['status']}"
        )

    print()
    print("PIPELINE STAGES")
    print("-" * 90)

    for index, stage in enumerate(
        report["pipeline_stages"],
        start=1
    ):
        print(
            f"{index:02d}. {stage}"
        )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 90)

    print("Source Data Modified: NO")
    print("Prediction Outputs Modified: NO")
    print("Model Artifacts Modified: NO")
    print("Recommendation Weights Modified: NO")
    print("Models Retrained: NO")
    print("Manager Decisions Modified: NO")
    print("Shipments Modified: NO")
    print("Database Modified: NO")
    print("Business Decision Executed: NO")


def save_report(report):
    with REPORT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4
        )


def main():
    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - "
        "AI END-TO-END PIPELINE VALIDATOR"
    )
    print("=" * 90)

    try:
        report = build_report()

        print_report(report)

        print()
        print("Saving validation report...")

        save_report(report)

        print("   ✓ Validation report saved.")

        print()
        print("=" * 90)
        print(
            "AI END-TO-END PIPELINE VALIDATION COMPLETED"
        )
        print("=" * 90)
        print(
            f"Report saved: {REPORT_FILE}"
        )
        print("=" * 90)

    except Exception as error:
        print()
        print("✗ Pipeline validation failed.")
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()