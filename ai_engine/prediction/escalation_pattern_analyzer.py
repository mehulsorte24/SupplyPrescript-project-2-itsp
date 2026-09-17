
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


BASE_DIR = Path(__file__).resolve().parent

HISTORY_FILE = BASE_DIR / "escalation_history.json"
OUTPUT_FILE = BASE_DIR / "escalation_pattern_report.json"

ENGINE_NAME = "AI Escalation Pattern Analyzer"
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


def extract_records(history_data):
    if not isinstance(history_data, dict):
        return []

    records = history_data.get(
        "records",
        []
    )

    if not isinstance(records, list):
        return []

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


def calculate_level_distribution(records):
    distribution = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "UNKNOWN": 0,
    }

    for record in records:
        level = normalize_level(
            record.get("escalation_level")
        )

        if level not in distribution:
            level = "UNKNOWN"

        distribution[level] += 1

    total = len(records)

    percentages = {}

    for level, count in distribution.items():
        if total > 0:
            percentages[f"{level}_PERCENTAGE"] = round(
                (count / total) * 100.0,
                2
            )
        else:
            percentages[f"{level}_PERCENTAGE"] = 0.0

    return {
        "counts": distribution,
        "percentages": percentages,
    }


def calculate_risk_level_distribution(records):
    distribution = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "UNKNOWN": 0,
    }

    for record in records:
        level = normalize_level(
            record.get("overall_risk_level")
        )

        if level not in distribution:
            level = "UNKNOWN"

        distribution[level] += 1

    return distribution


def calculate_average_metrics(records):
    if not records:
        return {
            "risk_exposure_score": 0.0,
            "escalation_score": 0.0,
            "delayed_percentage": 0.0,
            "critical_percentage": 0.0,
            "high_critical_percentage": 0.0,
            "delay_probability": 0.0,
            "expected_delay_days": 0.0,
            "confidence": 0.0,
            "intelligence": 0.0,
            "signal_count": 0.0,
        }

    def average(field):
        values = [
            safe_float(record.get(field))
            for record in records
        ]

        return round(
            mean(values),
            4
        )

    return {
        "risk_exposure_score": average(
            "risk_exposure_score"
        ),
        "escalation_score": average(
            "escalation_score"
        ),
        "delayed_percentage": average(
            "delayed_percentage"
        ),
        "critical_percentage": average(
            "critical_percentage"
        ),
        "high_critical_percentage": average(
            "high_critical_percentage"
        ),
        "delay_probability": average(
            "delay_probability"
        ),
        "expected_delay_days": average(
            "expected_delay_days"
        ),
        "confidence": average(
            "confidence"
        ),
        "intelligence": average(
            "intelligence"
        ),
        "signal_count": average(
            "signal_count"
        ),
    }


def calculate_frequency(records):
    if len(records) < 2:
        return {
            "records_analyzed": len(records),
            "intervals_available": 0,
            "average_interval_seconds": None,
            "minimum_interval_seconds": None,
            "maximum_interval_seconds": None,
            "frequency_status": "INSUFFICIENT_HISTORY",
        }

    timestamps = []

    for record in records:
        captured_at = record.get(
            "captured_at"
        )

        if not isinstance(captured_at, str):
            continue

        try:
            timestamp = datetime.fromisoformat(
                captured_at.replace(
                    "Z",
                    "+00:00"
                )
            )

            timestamps.append(timestamp)

        except ValueError:
            continue

    timestamps.sort()

    if len(timestamps) < 2:
        return {
            "records_analyzed": len(records),
            "intervals_available": 0,
            "average_interval_seconds": None,
            "minimum_interval_seconds": None,
            "maximum_interval_seconds": None,
            "frequency_status": "INSUFFICIENT_TIMESTAMP_DATA",
        }

    intervals = []

    for index in range(
        1,
        len(timestamps)
    ):
        delta = (
            timestamps[index]
            - timestamps[index - 1]
        ).total_seconds()

        if delta >= 0:
            intervals.append(delta)

    if not intervals:
        return {
            "records_analyzed": len(records),
            "intervals_available": 0,
            "average_interval_seconds": None,
            "minimum_interval_seconds": None,
            "maximum_interval_seconds": None,
            "frequency_status": "NO_VALID_INTERVALS",
        }

    return {
        "records_analyzed": len(records),
        "intervals_available": len(intervals),
        "average_interval_seconds": round(
            mean(intervals),
            2
        ),
        "minimum_interval_seconds": round(
            min(intervals),
            2
        ),
        "maximum_interval_seconds": round(
            max(intervals),
            2
        ),
        "frequency_status": "AVAILABLE",
    }


def analyze_recurring_critical_pattern(records):
    if not records:
        return {
            "critical_records": 0,
            "critical_percentage": 0.0,
            "pattern_status": "NO_HISTORY",
            "pattern_message": (
                "No escalation history is available."
            ),
        }

    critical_records = sum(
        1
        for record in records
        if normalize_level(
            record.get("escalation_level")
        ) == "CRITICAL"
    )

    critical_percentage = (
        critical_records
        / len(records)
    ) * 100.0

    if len(records) < 2:
        return {
            "critical_records": critical_records,
            "critical_percentage": round(
                critical_percentage,
                2
            ),
            "pattern_status": "BASELINE",
            "pattern_message": (
                "Only one escalation record exists; "
                "recurrence cannot yet be established."
            ),
        }

    if critical_percentage >= 75:
        status = "PERSISTENT_CRITICAL"
        message = (
            "Critical escalations dominate the available "
            "history."
        )

    elif critical_percentage >= 50:
        status = "FREQUENT_CRITICAL"
        message = (
            "Critical escalations occur frequently "
            "in the available history."
        )

    elif critical_percentage > 0:
        status = "OCCASIONAL_CRITICAL"
        message = (
            "Critical escalations are present but do not "
            "dominate the available history."
        )

    else:
        status = "NO_CRITICAL_PATTERN"
        message = (
            "No critical escalation pattern is present "
            "in the available history."
        )

    return {
        "critical_records": critical_records,
        "critical_percentage": round(
            critical_percentage,
            2
        ),
        "pattern_status": status,
        "pattern_message": message,
    }


def analyze_latest_record(records):
    if not records:
        return {
            "available": False,
            "latest_risk_level": "UNKNOWN",
            "latest_escalation_level": "UNKNOWN",
            "latest_risk_exposure_score": 0.0,
            "latest_escalation_score": 0.0,
        }

    latest = records[-1]

    return {
        "available": True,
        "latest_risk_level": normalize_level(
            latest.get(
                "overall_risk_level"
            )
        ),
        "latest_escalation_level": normalize_level(
            latest.get(
                "escalation_level"
            )
        ),
        "latest_risk_exposure_score": safe_float(
            latest.get(
                "risk_exposure_score"
            )
        ),
        "latest_escalation_score": safe_float(
            latest.get(
                "escalation_score"
            )
        ),
    }


def compare_latest_to_average(
    records,
    averages
):
    if not records:
        return {
            "available": False,
            "risk_exposure_change": 0.0,
            "escalation_score_change": 0.0,
            "delayed_percentage_change": 0.0,
            "critical_percentage_change": 0.0,
        }

    latest = records[-1]

    return {
        "available": True,
        "risk_exposure_change": round(
            safe_float(
                latest.get(
                    "risk_exposure_score"
                )
            )
            - averages["risk_exposure_score"],
            4
        ),
        "escalation_score_change": round(
            safe_float(
                latest.get(
                    "escalation_score"
                )
            )
            - averages["escalation_score"],
            4
        ),
        "delayed_percentage_change": round(
            safe_float(
                latest.get(
                    "delayed_percentage"
                )
            )
            - averages["delayed_percentage"],
            4
        ),
        "critical_percentage_change": round(
            safe_float(
                latest.get(
                    "critical_percentage"
                )
            )
            - averages["critical_percentage"],
            4
        ),
    }


def generate_pattern_signals(
    records,
    averages,
    level_distribution,
    risk_distribution,
    critical_pattern,
    frequency
):
    signals = []

    total_records = len(records)

    if total_records == 0:
        signals.append(
            "No escalation history is available for pattern analysis."
        )
        return signals

    critical_count = level_distribution[
        "counts"
    ]["CRITICAL"]

    critical_percentage = level_distribution[
        "percentages"
    ]["CRITICAL_PERCENTAGE"]

    high_count = level_distribution[
        "counts"
    ]["HIGH"]

    high_critical_count = (
        critical_count
        + high_count
    )

    high_critical_percentage = (
        high_critical_count
        / total_records
    ) * 100.0

    if critical_percentage >= 75:
        signals.append(
            "Critical escalation is persistent across the "
            "available history."
        )

    elif critical_percentage >= 50:
        signals.append(
            "Critical escalation appears frequently in the "
            "available history."
        )

    if high_critical_percentage >= 75:
        signals.append(
            "High and critical escalation levels dominate "
            "the available history."
        )

    if averages["risk_exposure_score"] >= 70:
        signals.append(
            "Average risk exposure remains at or above "
            "the critical monitoring threshold."
        )

    if averages["escalation_score"] >= 75:
        signals.append(
            "Average escalation score indicates sustained "
            "high-severity operational attention."
        )

    if averages["delayed_percentage"] >= 70:
        signals.append(
            "Delayed predictions remain high across the "
            "available escalation history."
        )

    if averages["critical_percentage"] >= 50:
        signals.append(
            "Critical prediction percentage remains high "
            "across the available history."
        )

    if averages["confidence"] < 0.50:
        signals.append(
            "Average AI confidence is below the healthy "
            "monitoring threshold."
        )

    if frequency["frequency_status"] == "INSUFFICIENT_HISTORY":
        signals.append(
            "Additional escalation records are required "
            "to establish temporal frequency patterns."
        )

    if total_records == 1:
        signals.append(
            "Only one escalation record exists; pattern "
            "analysis currently represents a baseline."
        )

    return signals


def determine_pattern_status(
    records,
    critical_pattern,
    averages
):
    if not records:
        return {
            "pattern_level": "NO_DATA",
            "pattern_status": "NO_HISTORY",
            "confidence": "NONE",
        }

    if len(records) == 1:
        return {
            "pattern_level": "BASELINE",
            "pattern_status": "INSUFFICIENT_HISTORY",
            "confidence": "LOW",
        }

    if (
        critical_pattern["pattern_status"]
        == "PERSISTENT_CRITICAL"
        and averages["escalation_score"] >= 75
    ):
        return {
            "pattern_level": "CRITICAL",
            "pattern_status": "PERSISTENT_HIGH_RISK",
            "confidence": "MEDIUM",
        }

    if (
        critical_pattern["pattern_status"]
        in {
            "PERSISTENT_CRITICAL",
            "FREQUENT_CRITICAL"
        }
    ):
        return {
            "pattern_level": "HIGH",
            "pattern_status": "RECURRING_ESCALATION",
            "confidence": "MEDIUM",
        }

    return {
        "pattern_level": "MONITORED",
        "pattern_status": "NO_DOMINANT_ESCALATION_PATTERN",
        "confidence": "MEDIUM",
    }


def build_operational_recommendation(
    pattern_status,
    records
):
    if not records:
        return (
            "Collect escalation history before drawing "
            "operational conclusions."
        )

    if len(records) == 1:
        return (
            "Continue monitoring escalation history. "
            "Additional batches are required before "
            "establishing recurring risk patterns."
        )

    if pattern_status["pattern_level"] == "CRITICAL":
        return (
            "Maintain immediate operational monitoring and "
            "prioritize recurring critical escalation events."
        )

    if pattern_status["pattern_level"] == "HIGH":
        return (
            "Maintain close operational monitoring and "
            "investigate recurring escalation patterns."
        )

    return (
        "Continue normal AI monitoring while accumulating "
        "additional escalation history."
    )


def build_report(
    records,
    averages,
    level_distribution,
    risk_distribution,
    frequency,
    critical_pattern,
    latest,
    latest_comparison,
    signals,
    pattern_status
):
    return {
        "analyzer": ENGINE_NAME,
        "analyzer_version": ENGINE_VERSION,
        "status": "COMPLETED",
        "analyzed_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "records_analyzed": len(records),

        "escalation_level_distribution": (
            level_distribution
        ),

        "risk_level_distribution": (
            risk_distribution
        ),

        "average_metrics": averages,

        "history_frequency": frequency,

        "critical_pattern_analysis": (
            critical_pattern
        ),

        "latest_record_analysis": latest,

        "latest_vs_historical_average": (
            latest_comparison
        ),

        "pattern_signals": signals,

        "pattern_assessment": pattern_status,

        "operational_recommendation": (
            build_operational_recommendation(
                pattern_status,
                records
            )
        ),

        "operational_safety": {
            "history_modified": False,
            "risk_report_modified": False,
            "prediction_outputs_modified": False,
            "models_modified": False,
            "retraining_triggered": False,
            "optimization_modified": False,
            "database_modified": False,
        },
    }


def save_report(report):
    try:
        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=2
            )

        return True

    except OSError as exc:
        print(
            "   ✗ Failed to save pattern report:"
        )
        print(
            f"     {exc}"
        )
        return False


def print_summary(
    records,
    averages,
    level_distribution,
    risk_distribution,
    frequency,
    critical_pattern,
    latest,
    latest_comparison,
    signals,
    pattern_status
):
    print()
    print("=" * 100)
    print(
        "SUPPLYPRESCRIPT - AI ESCALATION PATTERN ANALYZER"
    )
    print("=" * 100)

    print()
    print("HISTORY OVERVIEW")
    print("-" * 100)

    print(
        f"Records Analyzed         : "
        f"{len(records)}"
    )

    print()
    print("ESCALATION LEVEL DISTRIBUTION")
    print("-" * 100)

    counts = level_distribution["counts"]
    percentages = level_distribution["percentages"]

    print(
        f"CRITICAL                 : "
        f"{counts['CRITICAL']} "
        f"({percentages['CRITICAL_PERCENTAGE']:.2f}%)"
    )

    print(
        f"HIGH                     : "
        f"{counts['HIGH']} "
        f"({percentages['HIGH_PERCENTAGE']:.2f}%)"
    )

    print(
        f"MEDIUM                   : "
        f"{counts['MEDIUM']} "
        f"({percentages['MEDIUM_PERCENTAGE']:.2f}%)"
    )

    print(
        f"LOW                      : "
        f"{counts['LOW']} "
        f"({percentages['LOW_PERCENTAGE']:.2f}%)"
    )

    print()
    print("AVERAGE METRICS")
    print("-" * 100)

    print(
        f"Risk Exposure            : "
        f"{averages['risk_exposure_score']:.2f}%"
    )

    print(
        f"Escalation Score         : "
        f"{averages['escalation_score']:.2f}%"
    )

    print(
        f"Delayed Percentage       : "
        f"{averages['delayed_percentage']:.2f}%"
    )

    print(
        f"Critical Percentage      : "
        f"{averages['critical_percentage']:.2f}%"
    )

    print(
        f"High/Critical Percentage : "
        f"{averages['high_critical_percentage']:.2f}%"
    )

    print(
        f"Delay Probability        : "
        f"{averages['delay_probability']:.4f}"
    )

    print(
        f"Expected Delay Days      : "
        f"{averages['expected_delay_days']:.4f}"
    )

    print(
        f"AI Confidence            : "
        f"{averages['confidence']:.4f}"
    )

    print(
        f"AI Intelligence          : "
        f"{averages['intelligence']:.4f}"
    )

    print()
    print("HISTORY FREQUENCY")
    print("-" * 100)

    print(
        f"Intervals Available      : "
        f"{frequency['intervals_available']}"
    )

    if frequency["average_interval_seconds"] is None:
        print(
            "Average Interval         : "
            "Not available"
        )
    else:
        print(
            f"Average Interval         : "
            f"{frequency['average_interval_seconds']:.2f} seconds"
        )

    print(
        f"Frequency Status          : "
        f"{frequency['frequency_status']}"
    )

    print()
    print("CRITICAL PATTERN")
    print("-" * 100)

    print(
        f"Critical Records          : "
        f"{critical_pattern['critical_records']}"
    )

    print(
        f"Critical Percentage       : "
        f"{critical_pattern['critical_percentage']:.2f}%"
    )

    print(
        f"Pattern Status            : "
        f"{critical_pattern['pattern_status']}"
    )

    print(
        f"Pattern Message           : "
        f"{critical_pattern['pattern_message']}"
    )

    print()
    print("LATEST RECORD")
    print("-" * 100)

    if latest["available"]:
        print(
            f"Latest Risk Level        : "
            f"{latest['latest_risk_level']}"
        )

        print(
            f"Latest Escalation Level  : "
            f"{latest['latest_escalation_level']}"
        )

        print(
            f"Latest Risk Exposure     : "
            f"{latest['latest_risk_exposure_score']:.2f}%"
        )

        print(
            f"Latest Escalation Score  : "
            f"{latest['latest_escalation_score']:.2f}%"
        )
    else:
        print(
            "No latest record available."
        )

    print()
    print("LATEST VS HISTORICAL AVERAGE")
    print("-" * 100)

    print(
        f"Risk Exposure Change      : "
        f"{latest_comparison['risk_exposure_change']:+.4f}"
    )

    print(
        f"Escalation Score Change   : "
        f"{latest_comparison['escalation_score_change']:+.4f}"
    )

    print(
        f"Delayed % Change          : "
        f"{latest_comparison['delayed_percentage_change']:+.4f}"
    )

    print(
        f"Critical % Change         : "
        f"{latest_comparison['critical_percentage_change']:+.4f}"
    )

    print()
    print("PATTERN SIGNALS")
    print("-" * 100)

    if signals:
        for index, signal in enumerate(
            signals,
            start=1
        ):
            print(
                f"{index:02d}. {signal}"
            )
    else:
        print(
            "No pattern signals detected."
        )

    print()
    print("PATTERN ASSESSMENT")
    print("-" * 100)

    print(
        f"Pattern Level             : "
        f"{pattern_status['pattern_level']}"
    )

    print(
        f"Pattern Status            : "
        f"{pattern_status['pattern_status']}"
    )

    print(
        f"Analysis Confidence       : "
        f"{pattern_status['confidence']}"
    )

    print()
    print("OPERATIONAL SAFETY")
    print("-" * 100)

    print(
        "✓ Escalation history was not modified."
    )

    print(
        "✓ Risk reports were not modified."
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
        "✓ AI escalation pattern analysis completed successfully."
    )
    print(
        f"✓ Report saved: {OUTPUT_FILE}"
    )
    print("=" * 100)


def main():
    history_data = load_json_file(
        HISTORY_FILE,
        "AI escalation history"
    )

    if history_data is None:
        return

    print()
    print(
        "Extracting escalation history records..."
    )

    records = extract_records(
        history_data
    )

    print(
        f"   ✓ Records extracted: {len(records)}"
    )

    print()
    print(
        "Calculating escalation level distribution..."
    )

    level_distribution = (
        calculate_level_distribution(
            records
        )
    )

    print(
        "   ✓ Escalation distribution calculated."
    )

    print()
    print(
        "Calculating risk level distribution..."
    )

    risk_distribution = (
        calculate_risk_level_distribution(
            records
        )
    )

    print(
        "   ✓ Risk distribution calculated."
    )

    print()
    print(
        "Calculating average AI risk metrics..."
    )

    averages = calculate_average_metrics(
        records
    )

    print(
        "   ✓ Average metrics calculated."
    )

    print()
    print(
        "Analyzing history frequency..."
    )

    frequency = calculate_frequency(
        records
    )

    print(
        "   ✓ History frequency analyzed."
    )

    print()
    print(
        "Analyzing recurring critical patterns..."
    )

    critical_pattern = (
        analyze_recurring_critical_pattern(
            records
        )
    )

    print(
        "   ✓ Critical pattern analysis completed."
    )

    print()
    print(
        "Analyzing latest escalation record..."
    )

    latest = analyze_latest_record(
        records
    )

    latest_comparison = (
        compare_latest_to_average(
            records,
            averages
        )
    )

    print(
        "   ✓ Latest record analysis completed."
    )

    print()
    print(
        "Generating pattern signals..."
    )

    signals = generate_pattern_signals(
        records,
        averages,
        level_distribution,
        risk_distribution,
        critical_pattern,
        frequency
    )

    print(
        f"   ✓ Pattern signals generated: "
        f"{len(signals)}"
    )

    print()
    print(
        "Determining overall pattern assessment..."
    )

    pattern_status = determine_pattern_status(
        records,
        critical_pattern,
        averages
    )

    print(
        f"   ✓ Pattern level: "
        f"{pattern_status['pattern_level']}"
    )

    report = build_report(
        records,
        averages,
        level_distribution,
        risk_distribution,
        frequency,
        critical_pattern,
        latest,
        latest_comparison,
        signals,
        pattern_status
    )

    print()
    print(
        "Saving pattern analysis report..."
    )

    if not save_report(report):
        return

    print(
        "   ✓ Pattern report saved."
    )

    print_summary(
        records,
        averages,
        level_distribution,
        risk_distribution,
        frequency,
        critical_pattern,
        latest,
        latest_comparison,
        signals,
        pattern_status
    )


if __name__ == "__main__":
    main()

