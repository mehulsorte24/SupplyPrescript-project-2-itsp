import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

RISK_ESCALATION_REPORT = (
    BASE_DIR / "batch_risk_escalation_report.json"
)

HISTORY_FILE = (
    BASE_DIR / "escalation_history.json"
)

ENGINE_NAME = "AI Risk Escalation History Engine"
ENGINE_VERSION = "1.0"


def load_json_file(file_path: Path, description: str):
    print(f"Searching for {description}...")

    if not file_path.exists():
        print("   ✗ File not found:")
        print(f"     {file_path}")
        return None

    try:
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        print(f"   ✓ {description.capitalize()} loaded.")
        print(f"     {file_path}")

        return data

    except json.JSONDecodeError as exc:
        print("   ✗ Failed to parse file:")
        print(f"     {exc}")
        return None

    except OSError as exc:
        print("   ✗ Failed to read file:")
        print(f"     {exc}")
        return None


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_level(value):
    if not isinstance(value, str):
        return "UNKNOWN"

    return value.strip().upper()


def load_existing_history():
    if not HISTORY_FILE.exists():
        return {
            "history_engine": ENGINE_NAME,
            "history_version": ENGINE_VERSION,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_records": 0,
            "records": [],
        }

    try:
        with HISTORY_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            history = json.load(file)

    except (json.JSONDecodeError, OSError):
        print(
            "   ⚠ Existing escalation history could not "
            "be loaded."
        )
        print(
            "   ✓ Starting a new escalation history."
        )

        return {
            "history_engine": ENGINE_NAME,
            "history_version": ENGINE_VERSION,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_records": 0,
            "records": [],
        }

    if not isinstance(history, dict):
        history = {}

    records = history.get("records", [])

    if not isinstance(records, list):
        records = []

    history.setdefault(
        "history_engine",
        ENGINE_NAME
    )

    history.setdefault(
        "history_version",
        ENGINE_VERSION
    )

    history.setdefault(
        "created_at",
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    history["records"] = records
    history["total_records"] = len(records)

    return history


def extract_escalation_record(report):
    current_batch = report.get(
        "current_batch_risk",
        {}
    )

    trend = report.get(
        "risk_trend",
        {}
    )

    escalation = report.get(
        "escalation",
        {}
    )

    signals = report.get(
        "escalation_signals",
        []
    )

    if not isinstance(signals, list):
        signals = []

    return {
        "record_id": datetime.now(
            timezone.utc
        ).strftime(
            "ESC-%Y%m%d%H%M%S%f"
        ),
        "captured_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "total_predictions": safe_int(
            current_batch.get(
                "total_predictions"
            )
        ),

        "overall_risk_level": normalize_level(
            current_batch.get(
                "overall_risk_level"
            )
        ),

        "risk_exposure_score": safe_float(
            current_batch.get(
                "risk_exposure_score"
            )
        ),

        "delayed_percentage": safe_float(
            current_batch.get(
                "delayed_percentage"
            )
        ),

        "critical_percentage": safe_float(
            current_batch.get(
                "critical_percentage"
            )
        ),

        "high_critical_percentage": safe_float(
            current_batch.get(
                "high_critical_percentage"
            )
        ),

        "delay_probability": safe_float(
            current_batch.get(
                "delay_probability"
            )
        ),

        "expected_delay_days": safe_float(
            current_batch.get(
                "expected_delay_days"
            )
        ),

        "confidence": safe_float(
            current_batch.get(
                "confidence"
            )
        ),

        "intelligence": safe_float(
            current_batch.get(
                "intelligence"
            )
        ),

        "trend_status": normalize_level(
            trend.get(
                "trend_status"
            )
        ),

        "trend_direction": normalize_level(
            trend.get(
                "trend_direction"
            )
        ),

        "risk_change": safe_float(
            trend.get(
                "risk_change"
            )
        ),

        "trend_confidence": normalize_level(
            trend.get(
                "trend_confidence"
            )
        ),

        "escalation_score": safe_float(
            escalation.get(
                "escalation_score"
            )
        ),

        "escalation_level": normalize_level(
            escalation.get(
                "escalation_level"
            )
        ),

        "recommended_action": normalize_level(
            escalation.get(
                "recommended_action"
            )
        ),

        "signal_count": len(signals),

        "operational_recommendation": report.get(
            "operational_recommendation",
            ""
        ),
    }


def is_duplicate_record(history, new_record):
    records = history.get(
        "records",
        []
    )

    if not records:
        return False

    latest = records[-1]

    comparison_fields = [
        "total_predictions",
        "overall_risk_level",
        "risk_exposure_score",
        "delayed_percentage",
        "critical_percentage",
        "escalation_score",
        "escalation_level",
    ]

    return all(
        latest.get(field) == new_record.get(field)
        for field in comparison_fields
    )


def calculate_history_summary(records):
    if not records:
        return {
            "total_records": 0,
            "average_risk_exposure_score": 0.0,
            "average_escalation_score": 0.0,
            "average_delayed_percentage": 0.0,
            "average_critical_percentage": 0.0,
            "critical_escalations": 0,
            "high_escalations": 0,
            "medium_escalations": 0,
            "low_escalations": 0,
            "latest_risk_level": "UNKNOWN",
            "latest_escalation_level": "UNKNOWN",
        }

    risk_exposure_values = [
        safe_float(
            record.get(
                "risk_exposure_score"
            )
        )
        for record in records
    ]

    escalation_values = [
        safe_float(
            record.get(
                "escalation_score"
            )
        )
        for record in records
    ]

    delayed_values = [
        safe_float(
            record.get(
                "delayed_percentage"
            )
        )
        for record in records
    ]

    critical_values = [
        safe_float(
            record.get(
                "critical_percentage"
            )
        )
        for record in records
    ]

    critical_count = sum(
        1
        for record in records
        if normalize_level(
            record.get(
                "escalation_level"
            )
        ) == "CRITICAL"
    )

    high_count = sum(
        1
        for record in records
        if normalize_level(
            record.get(
                "escalation_level"
            )
        ) == "HIGH"
    )

    medium_count = sum(
        1
        for record in records
        if normalize_level(
            record.get(
                "escalation_level"
            )
        ) == "MEDIUM"
    )

    low_count = sum(
        1
        for record in records
        if normalize_level(
            record.get(
                "escalation_level"
            )
        ) == "LOW"
    )

    return {
        "total_records": len(records),

        "average_risk_exposure_score": round(
            sum(risk_exposure_values)
            / len(risk_exposure_values),
            2
        ),

        "average_escalation_score": round(
            sum(escalation_values)
            / len(escalation_values),
            2
        ),

        "average_delayed_percentage": round(
            sum(delayed_values)
            / len(delayed_values),
            2
        ),

        "average_critical_percentage": round(
            sum(critical_values)
            / len(critical_values),
            2
        ),

        "critical_escalations": critical_count,
        "high_escalations": high_count,
        "medium_escalations": medium_count,
        "low_escalations": low_count,

        "latest_risk_level": normalize_level(
            records[-1].get(
                "overall_risk_level"
            )
        ),

        "latest_escalation_level": normalize_level(
            records[-1].get(
                "escalation_level"
            )
        ),
    }


def build_history_report(
    history,
    new_record,
    duplicate
):
    records = history.get(
        "records",
        []
    )

    summary = calculate_history_summary(
        records
    )

    return {
        "history_engine": ENGINE_NAME,
        "history_version": ENGINE_VERSION,
        "status": "COMPLETED",

        "record_added": not duplicate,

        "current_record": new_record,

        "history_summary": summary,

        "history_storage": {
            "total_records": len(records),
            "history_file": str(
                HISTORY_FILE
            ),
        },

        "operational_safety": {
            "risk_report_modified": False,
            "prediction_outputs_modified": False,
            "models_modified": False,
            "retraining_triggered": False,
            "optimization_modified": False,
            "database_modified": False,
        },
    }


def save_history(history):
    try:
        with HISTORY_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                history,
                file,
                indent=2
            )

        return True

    except OSError as exc:
        print(
            "   ✗ Failed to save escalation history:"
        )
        print(
            f"     {exc}"
        )
        return False


def print_summary(
    record,
    history,
    duplicate
):
    records = history.get(
        "records",
        []
    )

    summary = calculate_history_summary(
        records
    )

    print()
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI RISK ESCALATION HISTORY ENGINE"
    )
    print("=" * 100)

    print()
    print("CURRENT ESCALATION RECORD")
    print("-" * 100)

    print(
        f"Record ID                : "
        f"{record['record_id']}"
    )

    print(
        f"Total Predictions        : "
        f"{record['total_predictions']}"
    )

    print(
        f"Overall Risk Level       : "
        f"{record['overall_risk_level']}"
    )

    print(
        f"Risk Exposure Score      : "
        f"{record['risk_exposure_score']:.2f}%"
    )

    print(
        f"Delayed Percentage       : "
        f"{record['delayed_percentage']:.2f}%"
    )

    print(
        f"Critical Percentage      : "
        f"{record['critical_percentage']:.2f}%"
    )

    print(
        f"Escalation Score         : "
        f"{record['escalation_score']:.2f}%"
    )

    print(
        f"Escalation Level         : "
        f"{record['escalation_level']}"
    )

    print(
        f"Signal Count             : "
        f"{record['signal_count']}"
    )

    print()
    print("HISTORY STATUS")
    print("-" * 100)

    if duplicate:
        print(
            "Record Status            : DUPLICATE - NOT ADDED"
        )
    else:
        print(
            "Record Status            : NEW RECORD ADDED"
        )

    print(
        f"Total History Records    : "
        f"{summary['total_records']}"
    )

    print()
    print("ESCALATION HISTORY SUMMARY")
    print("-" * 100)

    print(
        f"Average Risk Exposure    : "
        f"{summary['average_risk_exposure_score']:.2f}%"
    )

    print(
        f"Average Escalation Score : "
        f"{summary['average_escalation_score']:.2f}%"
    )

    print(
        f"Average Delayed %        : "
        f"{summary['average_delayed_percentage']:.2f}%"
    )

    print(
        f"Average Critical %       : "
        f"{summary['average_critical_percentage']:.2f}%"
    )

    print(
        f"Critical Escalations     : "
        f"{summary['critical_escalations']}"
    )

    print(
        f"High Escalations         : "
        f"{summary['high_escalations']}"
    )

    print(
        f"Medium Escalations       : "
        f"{summary['medium_escalations']}"
    )

    print(
        f"Low Escalations          : "
        f"{summary['low_escalations']}"
    )

    print(
        f"Latest Risk Level        : "
        f"{summary['latest_risk_level']}"
    )

    print(
        f"Latest Escalation Level  : "
        f"{summary['latest_escalation_level']}"
    )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 100)

    print(
        "✓ Risk aggregation report was not modified."
    )

    print(
        "✓ Prediction outputs were not modified."
    )

    print(
        "✓ Models were not modified."
    )

    print(
        "✓ Retraining was not triggered."
    )

    print(
        "✓ Optimization was not modified."
    )

    print(
        "✓ Database records were not modified."
    )

    print()
    print("=" * 100)
    print(
        "✓ AI risk escalation history analysis completed."
    )
    print(
        f"✓ History saved: {HISTORY_FILE}"
    )
    print("=" * 100)


def main():
    risk_report = load_json_file(
        RISK_ESCALATION_REPORT,
        "AI batch risk escalation report"
    )

    if risk_report is None:
        return

    print()
    print(
        "Extracting escalation decision..."
    )

    new_record = extract_escalation_record(
        risk_report
    )

    print(
        "   ✓ Escalation decision extracted."
    )

    print()
    print(
        "Loading escalation history..."
    )

    history = load_existing_history()

    print(
        f"   ✓ Existing history records: "
        f"{len(history.get('records', []))}"
    )

    duplicate = is_duplicate_record(
        history,
        new_record
    )

    if duplicate:
        print()
        print(
            "   ⚠ Current escalation already exists "
            "as the latest history record."
        )
        print(
            "   ✓ Duplicate record will not be added."
        )
    else:
        print()
        print(
            "Adding new escalation record..."
        )

        history["records"].append(
            new_record
        )

        history["total_records"] = len(
            history["records"]
        )

        history["updated_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        if save_history(history):
            print(
                "   ✓ New escalation record added."
            )
        else:
            return

    if duplicate:
        history["total_records"] = len(
            history["records"]
        )

    history_report = build_history_report(
        history,
        new_record,
        duplicate
    )

    print_summary(
        new_record,
        history,
        duplicate
    )


if __name__ == "__main__":
    main()