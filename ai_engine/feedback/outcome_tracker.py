import csv
import json
import os
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

PREDICTION_DIR = os.path.join(
    BASE_DIR,
    "ai_engine",
    "prediction"
)

ACTUAL_DATA_FILE = os.path.join(
    BASE_DIR,
    "ai_engine",
    "data",
    "raw",
    "shipments.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "ai_engine",
    "feedback",
    "prediction_outcomes.json"
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_utc_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(UTC).isoformat()


def load_json_file(file_path: str) -> Any:
    """Load JSON data from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """Load CSV records as a list of dictionaries."""
    records = []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            records.append(dict(row))

    return records


def save_json_file(
    file_path: str,
    data: Any
) -> None:
    """Save data as formatted JSON."""
    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# =============================================================================
# RECORD EXTRACTION
# =============================================================================

def find_records(
    data: Any
) -> List[Dict[str, Any]]:
    """
    Extract shipment records from different JSON structures.
    """

    records = []

    if isinstance(data, list):

        for item in data:

            if isinstance(item, dict):
                records.append(item)

        return records

    if isinstance(data, dict):

        # Direct shipment record
        if (
            "shipment_id" in data
            or "shipmentId" in data
            or "ShipmentID" in data
        ):
            return [data]

        # Common container keys
        for key in [
            "predictions",
            "prediction",
            "outcomes",
            "shipments",
            "records",
            "results",
            "data",
            "items"
        ]:

            value = data.get(key)

            if isinstance(value, list):

                for item in value:

                    if isinstance(item, dict):
                        records.append(item)

                if records:
                    return records

            elif isinstance(value, dict):

                nested_records = find_records(
                    value
                )

                if nested_records:
                    return nested_records

    return records


# =============================================================================
# FIELD EXTRACTION
# =============================================================================

def get_shipment_id(
    record: Dict[str, Any]
) -> Optional[str]:
    """Extract shipment ID from a record."""

    possible_keys = [
        "shipment_id",
        "shipmentId",
        "ShipmentID",
        "ShipmentId",
        "SHIPMENT_ID",
        "id",
        "ID"
    ]

    for key in possible_keys:

        if key in record:

            value = record[key]

            if value is not None:

                value = str(value).strip()

                if value:
                    return value

    return None


def get_prediction_status(
    record: Dict[str, Any]
) -> Optional[str]:
    """Extract predicted shipment status."""

    prediction = record.get(
        "prediction"
    )

    # Expected SupplyPrescript structure:
    #
    # "prediction": {
    #     "prediction": "ON_TIME"
    # }

    if isinstance(
        prediction,
        dict
    ):

        value = prediction.get(
            "prediction"
        )

        if value is not None:

            return str(
                value
            ).strip().upper()

        for key in [
            "status",
            "predicted_status",
            "predicted_outcome",
            "result"
        ]:

            if key in prediction:

                value = prediction[key]

                if value is not None:

                    return str(
                        value
                    ).strip().upper()

    elif isinstance(
        prediction,
        str
    ):

        return prediction.strip().upper()

    # Fallback for flat structures
    for key in [
        "predicted_status",
        "predicted_outcome",
        "prediction_status",
        "status_prediction",
        "prediction",
        "PredictedStatus"
    ]:

        if key in record:

            value = record[key]

            if isinstance(
                value,
                str
            ):

                return value.strip().upper()

    return None


def get_actual_status(
    record: Dict[str, Any]
) -> Optional[str]:
    """Extract actual shipment status."""

    # Your actual CSV uses:
    #
    # delay_status
    #
    # Example:
    # delay_status = DELAYED

    possible_keys = [
        "delay_status",
        "actual_status",
        "actual_outcome",
        "actual_result",
        "outcome",
        "status",
        "delivery_status",
        "actualStatus",
        "ActualStatus",
        "result"
    ]

    for key in possible_keys:

        if key not in record:
            continue

        value = record[key]

        if value is None:
            continue

        if isinstance(
            value,
            dict
        ):

            for nested_key in [
                "status",
                "actual_status",
                "delay_status",
                "outcome",
                "result"
            ]:

                nested_value = value.get(
                    nested_key
                )

                if nested_value is not None:

                    return str(
                        nested_value
                    ).strip().upper()

        else:

            return str(
                value
            ).strip().upper()

    return None


def get_predicted_delay(
    record: Dict[str, Any]
) -> Optional[float]:
    """Extract predicted delay in days."""

    prediction = record.get(
        "prediction"
    )

    if isinstance(
        prediction,
        dict
    ):

        for key in [
            "expected_delay_days",
            "predicted_delay_days",
            "predicted_delay",
            "delay_prediction",
            "estimated_delay",
            "delay_days"
        ]:

            if key in prediction:

                try:

                    return float(
                        prediction[key]
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    pass

    # Fallback for flat structures
    for key in [
        "expected_delay_days",
        "predicted_delay_days",
        "predicted_delay",
        "delay_prediction",
        "estimated_delay",
        "delay_days",
        "PredictedDelay"
    ]:

        if key in record:

            try:

                return float(
                    record[key]
                )

            except (
                TypeError,
                ValueError
            ):

                pass

    return None


def get_actual_delay(
    record: Dict[str, Any]
) -> Optional[float]:
    """Extract actual delay in days."""

    # Your actual CSV uses:
    #
    # actual_delay_days

    possible_keys = [
        "actual_delay_days",
        "actual_delay",
        "delay_days",
        "actual_days",
        "delay",
        "ActualDelay",
        "ActualDelayDays"
    ]

    for key in possible_keys:

        if key not in record:
            continue

        value = record[key]

        if value is None:
            continue

        if str(value).strip() == "":
            continue

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            continue

    return None


# =============================================================================
# STATUS NORMALIZATION
# =============================================================================

def normalize_status(
    status: Optional[str]
) -> Optional[str]:
    """Normalize different status formats."""

    if status is None:
        return None

    value = str(
        status
    ).strip().upper()

    value = value.replace(
        "-",
        "_"
    )

    value = value.replace(
        " ",
        "_"
    )

    mapping = {

        "ON_TIME": "ON_TIME",
        "ONTIME": "ON_TIME",
        "ON_TIME_DELIVERY": "ON_TIME",
        "DELIVERED_ON_TIME": "ON_TIME",

        "DELAYED": "DELAYED",
        "DELAY": "DELAYED",
        "LATE": "DELAYED",
        "DELIVERED_LATE": "DELAYED",
        "DELIVERY_DELAYED": "DELAYED"
    }

    return mapping.get(
        value,
        value
    )


# =============================================================================
# OUTCOME LOOKUP
# =============================================================================

def create_outcome_lookup(
    outcomes: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Create a shipment ID based lookup."""

    lookup = {}

    for outcome in outcomes:

        shipment_id = get_shipment_id(
            outcome
        )

        if shipment_id:

            lookup[shipment_id] = outcome

    return lookup


# =============================================================================
# SINGLE PREDICTION EVALUATION
# =============================================================================

def evaluate_prediction(
    prediction: Dict[str, Any],
    actual: Dict[str, Any]
) -> Dict[str, Any]:
    """Compare one prediction against its actual result."""

    shipment_id = get_shipment_id(
        prediction
    )

    predicted_status = normalize_status(
        get_prediction_status(
            prediction
        )
    )

    actual_status = normalize_status(
        get_actual_status(
            actual
        )
    )

    predicted_delay = get_predicted_delay(
        prediction
    )

    actual_delay = get_actual_delay(
        actual
    )

    # -------------------------------------------------------------------------
    # CLASSIFICATION EVALUATION
    # -------------------------------------------------------------------------

    classification_correct = None

    if (
        predicted_status is not None
        and actual_status is not None
    ):

        classification_correct = (
            predicted_status == actual_status
        )

    # -------------------------------------------------------------------------
    # DELAY ERROR
    # -------------------------------------------------------------------------

    delay_error = None

    if (
        predicted_delay is not None
        and actual_delay is not None
    ):

        delay_error = abs(
            predicted_delay - actual_delay
        )

    return {

        "shipment_id": shipment_id,

        "prediction": {
            "status": predicted_status,
            "delay_days": (
                round(
                    predicted_delay,
                    4
                )
                if predicted_delay is not None
                else None
            )
        },

        "actual": {
            "status": actual_status,
            "delay_days": (
                round(
                    actual_delay,
                    4
                )
                if actual_delay is not None
                else None
            )
        },

        "evaluation": {

            "classification_correct":
                classification_correct,

            "absolute_delay_error_days":
                (
                    round(
                        delay_error,
                        4
                    )
                    if delay_error is not None
                    else None
                )
        },

        "evaluated_at":
            get_utc_timestamp()
    }


# =============================================================================
# EVALUATE ALL PREDICTIONS
# =============================================================================

def evaluate_predictions(
    predictions: List[Dict[str, Any]],
    outcomes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Match predictions and actual outcomes by shipment ID."""

    lookup = create_outcome_lookup(
        outcomes
    )

    evaluated = []

    for prediction in predictions:

        shipment_id = get_shipment_id(
            prediction
        )

        if not shipment_id:
            continue

        actual = lookup.get(
            shipment_id
        )

        if actual is None:
            continue

        evaluated.append(
            evaluate_prediction(
                prediction,
                actual
            )
        )

    return evaluated


# =============================================================================
# METRICS
# =============================================================================

def calculate_metrics(
    evaluated_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate feedback metrics."""

    correct = 0
    incorrect = 0

    delay_errors = []

    for record in evaluated_records:

        evaluation = record.get(
            "evaluation",
            {}
        )

        classification = evaluation.get(
            "classification_correct"
        )

        if classification is True:

            correct += 1

        elif classification is False:

            incorrect += 1

        delay_error = evaluation.get(
            "absolute_delay_error_days"
        )

        if delay_error is not None:

            delay_errors.append(
                float(delay_error)
            )

    classification_total = (
        correct + incorrect
    )

    accuracy = (
        (
            correct /
            classification_total
        ) * 100
        if classification_total > 0
        else 0.0
    )

    mean_delay_error = (
        sum(delay_errors) /
        len(delay_errors)
        if delay_errors
        else 0.0
    )

    return {

        "evaluated_records":
            len(evaluated_records),

        "correct_predictions":
            correct,

        "incorrect_predictions":
            incorrect,

        "classification_accuracy_percent":
            round(
                accuracy,
                2
            ),

        "mean_absolute_delay_error_days":
            round(
                mean_delay_error,
                2
            ),

        "delay_evaluations":
            len(delay_errors)
    }


# =============================================================================
# FEEDBACK GENERATION
# =============================================================================

def generate_feedback(
    metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate qualitative feedback from metrics."""

    accuracy = metrics[
        "classification_accuracy_percent"
    ]

    delay_error = metrics[
        "mean_absolute_delay_error_days"
    ]

    # -------------------------------------------------------------------------
    # ACCURACY ASSESSMENT
    # -------------------------------------------------------------------------

    if accuracy >= 90:

        accuracy_assessment = "Excellent"

    elif accuracy >= 80:

        accuracy_assessment = "Good"

    elif accuracy >= 70:

        accuracy_assessment = "Moderate"

    elif accuracy >= 60:

        accuracy_assessment = "Needs Improvement"

    else:

        accuracy_assessment = "Poor"

    # -------------------------------------------------------------------------
    # DELAY ASSESSMENT
    # -------------------------------------------------------------------------

    if delay_error <= 0.25:

        delay_assessment = "Excellent"

    elif delay_error <= 0.50:

        delay_assessment = "Good"

    elif delay_error <= 1.00:

        delay_assessment = "Moderate"

    else:

        delay_assessment = "Needs Improvement"

    recommendations = []

    if accuracy < 80:

        recommendations.append(
            "Review and improve shipment delay classification performance."
        )

    else:

        recommendations.append(
            "Classification performance is acceptable."
        )

    if delay_error > 1.0:

        recommendations.append(
            "Improve expected delay estimation."
        )

    else:

        recommendations.append(
            "Delay prediction error is within an acceptable range."
        )

    recommendations.append(
        "Continue collecting actual shipment outcomes for future model feedback."
    )

    return {

        "accuracy_assessment":
            accuracy_assessment,

        "delay_prediction_assessment":
            delay_assessment,

        "recommendations":
            recommendations
    }


# =============================================================================
# OUTPUT CREATION
# =============================================================================

def create_output(
    evaluated_records: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    feedback: Dict[str, Any],
    prediction_file: str,
    actual_data_file: str
) -> Dict[str, Any]:
    """Create final feedback output."""

    return {

        "system":
            "SupplyPrescript",

        "module":
            "AI Feedback Engine",

        "generated_at":
            get_utc_timestamp(),

        "prediction_source":
            os.path.relpath(
                prediction_file,
                BASE_DIR
            ),

        "actual_data_source":
            os.path.relpath(
                actual_data_file,
                BASE_DIR
            ),

        "summary":
            metrics,

        "assessment":
            feedback,

        "evaluated_predictions":
            evaluated_records
    }


# =============================================================================
# FIND PREDICTION FILE
# =============================================================================

def find_prediction_file() -> str:
    """
    Automatically find the SupplyPrescript prediction JSON.

    Expected file:
    ai_engine/prediction/ai_intelligence_results.json
    """

    if not os.path.exists(
        PREDICTION_DIR
    ):

        raise FileNotFoundError(
            "Prediction directory not found:\n"
            f"{PREDICTION_DIR}"
        )

    # Prefer the known SupplyPrescript prediction file.
    preferred_file = os.path.join(
        PREDICTION_DIR,
        "ai_intelligence_results.json"
    )

    if os.path.exists(
        preferred_file
    ):

        return preferred_file

    ignored_names = {
        "prediction_outcomes.json",
        "model_feedback.json",
        "feedback.json",
        "outcomes.json"
    }

    candidates = []

    for root, _, files in os.walk(
        PREDICTION_DIR
    ):

        for filename in files:

            if not filename.lower().endswith(
                ".json"
            ):
                continue

            if filename.lower() in ignored_names:
                continue

            path = os.path.join(
                root,
                filename
            )

            try:

                data = load_json_file(
                    path
                )

                records = find_records(
                    data
                )

                prediction_count = 0

                for record in records:

                    shipment_id = get_shipment_id(
                        record
                    )

                    status = get_prediction_status(
                        record
                    )

                    delay = get_predicted_delay(
                        record
                    )

                    if (
                        shipment_id
                        and (
                            status is not None
                            or delay is not None
                        )
                    ):

                        prediction_count += 1

                if prediction_count > 0:

                    candidates.append(
                        (
                            prediction_count,
                            os.path.getmtime(path),
                            path
                        )
                    )

            except Exception:
                continue

    if not candidates:

        raise FileNotFoundError(
            "No usable SupplyPrescript prediction JSON file was found."
        )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    return candidates[0][2]


# =============================================================================
# VALIDATE ACTUAL DATA
# =============================================================================

def validate_actual_data(
    outcomes: List[Dict[str, Any]]
) -> None:
    """Validate that the actual CSV contains required fields."""

    if not outcomes:

        raise ValueError(
            "Actual shipment CSV contains no records."
        )

    sample = outcomes[0]

    required_fields = [
        "shipment_id",
        "actual_delay_days",
        "delay_status"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in sample
    ]

    if missing_fields:

        raise ValueError(
            "Actual shipment CSV is missing required fields: "
            + ", ".join(missing_fields)
        )


# =============================================================================
# PRINT HEADER
# =============================================================================

def print_header() -> None:

    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI FEEDBACK ENGINE"
    )
    print("=" * 100)
    print()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print_header()

    # =========================================================================
    # FIND PREDICTIONS
    # =========================================================================

    print(
        "Searching for AI prediction output..."
    )

    try:

        prediction_file = find_prediction_file()

        print(
            "   ✓ Prediction file found:"
        )

        print(
            f"     {prediction_file}"
        )

    except Exception as error:

        print(
            "   ✗ Failed to find prediction file:"
        )

        print(
            f"     {error}"
        )

        return

    # =========================================================================
    # LOAD PREDICTIONS
    # =========================================================================

    print()

    print(
        "Loading AI predictions..."
    )

    try:

        prediction_data = load_json_file(
            prediction_file
        )

        predictions = find_records(
            prediction_data
        )

        if not predictions:

            print(
                "   ✗ No prediction records found."
            )

            return

        print(
            f"   ✓ Predictions loaded: "
            f"{len(predictions)}"
        )

    except Exception as error:

        print(
            "   ✗ Failed to load predictions:"
        )

        print(
            f"     {error}"
        )

        return

    # =========================================================================
    # LOAD ACTUAL SHIPMENT DATA
    # =========================================================================

    print()

    print(
        "Loading actual shipment outcomes..."
    )

    if not os.path.exists(
        ACTUAL_DATA_FILE
    ):

        print(
            "   ✗ Actual shipment data file not found:"
        )

        print(
            f"     {ACTUAL_DATA_FILE}"
        )

        return

    try:

        outcomes = load_csv_file(
            ACTUAL_DATA_FILE
        )

        validate_actual_data(
            outcomes
        )

        print(
            f"   ✓ Shipment outcomes loaded: "
            f"{len(outcomes)}"
        )

        print(
            "   ✓ Source contains actual_delay_days "
            "and delay_status"
        )

    except Exception as error:

        print(
            "   ✗ Failed to load actual shipment data:"
        )

        print(
            f"     {error}"
        )

        return

    # =========================================================================
    # MATCH RECORDS
    # =========================================================================

    print()

    print(
        "Matching predictions with actual outcomes..."
    )

    evaluated_records = evaluate_predictions(
        predictions,
        outcomes
    )

    print(
        f"   ✓ Matched and evaluated: "
        f"{len(evaluated_records)}"
    )

    if not evaluated_records:

        print()

        print(
            "   ✗ No shipment IDs matched between"
        )

        print(
            "     prediction output and actual shipment data."
        )

        return

    # =========================================================================
    # METRICS
    # =========================================================================

    metrics = calculate_metrics(
        evaluated_records
    )

    # =========================================================================
    # FEEDBACK
    # =========================================================================

    feedback = generate_feedback(
        metrics
    )

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print()

    print(
        "FEEDBACK SUMMARY"
    )

    print("=" * 100)

    print(
        f"Evaluated records              : "
        f"{metrics['evaluated_records']}"
    )

    print(
        f"Correct predictions            : "
        f"{metrics['correct_predictions']}"
    )

    print(
        f"Incorrect predictions          : "
        f"{metrics['incorrect_predictions']}"
    )

    print(
        f"Classification accuracy        : "
        f"{metrics['classification_accuracy_percent']:.2f}%"
    )

    print(
        f"Mean absolute delay error      : "
        f"{metrics['mean_absolute_delay_error_days']:.2f} days"
    )

    print(
        f"Delay evaluations              : "
        f"{metrics['delay_evaluations']}"
    )

    print()

    print(
        f"Accuracy assessment            : "
        f"{feedback['accuracy_assessment']}"
    )

    print(
        f"Delay assessment               : "
        f"{feedback['delay_prediction_assessment']}"
    )

    print()

    print(
        "Recommendations:"
    )

    for recommendation in feedback[
        "recommendations"
    ]:

        print(
            f"   • {recommendation}"
        )

    # =========================================================================
    # SAVE FEEDBACK
    # =========================================================================

    output = create_output(
        evaluated_records,
        metrics,
        feedback,
        prediction_file,
        ACTUAL_DATA_FILE
    )

    try:

        save_json_file(
            OUTPUT_FILE,
            output
        )

        print()

        print(
            "✓ Feedback output saved:"
        )

        print(
            f"  {OUTPUT_FILE}"
        )

    except Exception as error:

        print()

        print(
            "✗ Failed to save feedback output:"
        )

        print(
            f"  {error}"
        )

        return

    # =========================================================================
    # COMPLETION
    # =========================================================================

    print()

    print("=" * 100)

    print(
        "AI FEEDBACK ENGINE COMPLETED"
    )

    print("=" * 100)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()