import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path.cwd()
PREDICTION_DIR = BASE_DIR / "ai_engine" / "prediction"

RISK_ESCALATION_REPORT = (
    PREDICTION_DIR / "batch_risk_escalation_report.json"
)

TREND_STATE_REPORT = (
    PREDICTION_DIR / "escalation_trend_state_report.json"
)

STATE_TRANSITION_REPORT = (
    PREDICTION_DIR / "escalation_trend_state_transition_report.json"
)

OUTPUT_REPORT = (
    PREDICTION_DIR / "decision_intelligence_report.json"
)


def load_json_file(file_path):
    """Load a JSON file safely."""

    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        print(f"   ✗ Invalid JSON in {file_path.name}: {error}")
        return None

    except OSError as error:
        print(f"   ✗ Failed to read {file_path.name}: {error}")
        return None


def safe_float(value, default=0.0):
    """Convert a value into a float safely."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_text(value, default="UNKNOWN"):
    """Convert a value into uppercase text."""

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text.upper()


def extract_risk_information(report):
    """Extract risk information from the actual batch risk escalation report."""

    if not isinstance(report, dict):
        return {
            "total_predictions": 0,
            "on_time": 0,
            "delayed": 0,
            "delayed_percentage": 0.0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
            "high_critical_percentage": 0.0,
            "critical_percentage": 0.0,
            "delay_probability": 0.0,
            "expected_delay_days": 0.0,
            "confidence": 0.0,
            "intelligence": 0.0,
            "risk_exposure_score": 0.0,
            "overall_risk_level": "UNKNOWN",
            "escalation_score": 0.0,
            "escalation_level": "UNKNOWN",
            "recommended_action": "UNKNOWN",
            "operational_recommendation": "UNKNOWN",
            "escalation_signals": [],
        }

    current_batch = report.get("current_batch_risk", {})

    if not isinstance(current_batch, dict):
        current_batch = {}

    escalation = report.get("escalation", {})

    if not isinstance(escalation, dict):
        escalation = {}

    escalation_signals = report.get(
        "escalation_signals",
        [],
    )

    if not isinstance(escalation_signals, list):
        escalation_signals = []

    return {
        "total_predictions": int(
            safe_float(
                current_batch.get(
                    "total_predictions",
                    0,
                )
            )
        ),
        "on_time": int(
            safe_float(
                current_batch.get(
                    "on_time",
                    0,
                )
            )
        ),
        "delayed": int(
            safe_float(
                current_batch.get(
                    "delayed",
                    0,
                )
            )
        ),
        "delayed_percentage": safe_float(
            current_batch.get(
                "delayed_percentage",
                0.0,
            )
        ),
        "low": int(
            safe_float(
                current_batch.get(
                    "low",
                    0,
                )
            )
        ),
        "medium": int(
            safe_float(
                current_batch.get(
                    "medium",
                    0,
                )
            )
        ),
        "high": int(
            safe_float(
                current_batch.get(
                    "high",
                    0,
                )
            )
        ),
        "critical": int(
            safe_float(
                current_batch.get(
                    "critical",
                    0,
                )
            )
        ),
        "high_critical_percentage": safe_float(
            current_batch.get(
                "high_critical_percentage",
                0.0,
            )
        ),
        "critical_percentage": safe_float(
            current_batch.get(
                "critical_percentage",
                0.0,
            )
        ),
        "delay_probability": safe_float(
            current_batch.get(
                "delay_probability",
                0.0,
            )
        ),
        "expected_delay_days": safe_float(
            current_batch.get(
                "expected_delay_days",
                0.0,
            )
        ),
        "confidence": safe_float(
            current_batch.get(
                "confidence",
                0.0,
            )
        ),
        "intelligence": safe_float(
            current_batch.get(
                "intelligence",
                0.0,
            )
        ),
        "risk_exposure_score": safe_float(
            current_batch.get(
                "risk_exposure_score",
                0.0,
            )
        ),
        "overall_risk_level": normalize_text(
            current_batch.get(
                "overall_risk_level",
                "UNKNOWN",
            )
        ),
        "escalation_score": safe_float(
            escalation.get(
                "escalation_score",
                0.0,
            )
        ),
        "escalation_level": normalize_text(
            escalation.get(
                "escalation_level",
                "UNKNOWN",
            )
        ),
        "recommended_action": normalize_text(
            escalation.get(
                "recommended_action",
                "UNKNOWN",
            )
        ),
        "operational_recommendation": report.get(
            "operational_recommendation",
            "UNKNOWN",
        ),
        "escalation_signals": escalation_signals,
    }


def extract_trend_information(report):
    """Extract trend-state information."""

    if not isinstance(report, dict):
        return {
            "state": "UNKNOWN",
            "confidence": "UNKNOWN",
            "operational_status": "UNKNOWN",
            "signals": [],
        }

    classification = report.get(
        "classification",
        {},
    )

    if not isinstance(classification, dict):
        classification = {}

    state = normalize_text(
        classification.get(
            "state",
            report.get(
                "state",
                "UNKNOWN",
            ),
        )
    )

    confidence = normalize_text(
        classification.get(
            "confidence",
            report.get(
                "confidence",
                "UNKNOWN",
            ),
        )
    )

    operational_status = normalize_text(
        report.get(
            "operational_status",
            classification.get(
                "source_persistence_status",
                "UNKNOWN",
            ),
        )
    )

    signals = report.get(
        "signals",
        [],
    )

    if not isinstance(signals, list):
        signals = []

    return {
        "state": state,
        "confidence": confidence,
        "operational_status": operational_status,
        "signals": signals,
    }


def extract_transition_information(report):
    """Extract state-transition information."""

    if not isinstance(report, dict):
        return {
            "status": "UNKNOWN",
            "confidence": "UNKNOWN",
            "transition_count": 0,
            "signals": [],
        }

    operational_analysis = report.get(
        "operational_analysis",
        {},
    )

    if not isinstance(operational_analysis, dict):
        operational_analysis = {}

    history_overview = report.get(
        "history_overview",
        {},
    )

    if not isinstance(history_overview, dict):
        history_overview = {}

    transition_count = history_overview.get(
        "transition_records",
        report.get(
            "transition_count",
            0,
        ),
    )

    try:
        transition_count = int(
            transition_count
        )
    except (TypeError, ValueError):
        transition_count = 0

    status = normalize_text(
        operational_analysis.get(
            "status",
            report.get(
                "operational_status",
                "UNKNOWN",
            ),
        )
    )

    confidence = normalize_text(
        operational_analysis.get(
            "confidence",
            report.get(
                "confidence",
                "UNKNOWN",
            ),
        )
    )

    signals = report.get(
        "transition_signals",
        [],
    )

    if not signals:
        signals = report.get(
            "signals",
            [],
        )

    if not isinstance(signals, list):
        signals = []

    return {
        "status": status,
        "confidence": confidence,
        "transition_count": transition_count,
        "signals": signals,
    }


def determine_priority(
    risk_info,
    trend_info,
    transition_info,
):
    """Determine overall decision priority."""

    overall_risk = risk_info[
        "overall_risk_level"
    ]

    escalation_level = risk_info[
        "escalation_level"
    ]

    risk_exposure = risk_info[
        "risk_exposure_score"
    ]

    escalation_score = risk_info[
        "escalation_score"
    ]

    if (
        overall_risk == "CRITICAL"
        or escalation_level == "CRITICAL"
        or risk_exposure >= 75
        or escalation_score >= 90
    ):
        return "CRITICAL"

    if (
        overall_risk == "HIGH"
        or escalation_level == "HIGH"
        or risk_exposure >= 50
        or escalation_score >= 70
    ):
        return "HIGH"

    if (
        overall_risk == "MEDIUM"
        or escalation_level == "MEDIUM"
        or risk_exposure >= 25
        or escalation_score >= 40
    ):
        return "MEDIUM"

    if (
        overall_risk == "LOW"
        or escalation_level == "LOW"
    ):
        return "LOW"

    if trend_info["state"] in {
        "ESCALATING",
        "DETERIORATING",
    }:
        return "HIGH"

    if transition_info[
        "transition_count"
    ] > 0:
        return "MEDIUM"

    return "UNKNOWN"


def determine_attention_level(priority):
    """Convert priority into a manager attention level."""

    attention_map = {
        "CRITICAL": "IMMEDIATE",
        "HIGH": "URGENT",
        "MEDIUM": "MONITOR_CLOSELY",
        "LOW": "ROUTINE",
        "UNKNOWN": "INSUFFICIENT_EVIDENCE",
    }

    return attention_map.get(
        priority,
        "INSUFFICIENT_EVIDENCE",
    )


def determine_primary_concern(
    risk_info,
    trend_info,
    transition_info,
):
    """Generate the main decision-support concern."""

    if risk_info[
        "overall_risk_level"
    ] == "CRITICAL":

        if (
            trend_info["operational_status"]
            == "INSUFFICIENT_HISTORY"
        ):
            return (
                "Current disruption risk is critical, "
                "while temporal trend evidence remains insufficient."
            )

        return (
            "Current supply-chain disruption exposure is critical."
        )

    if risk_info[
        "overall_risk_level"
    ] == "HIGH":

        return (
            "Current supply-chain disruption exposure is elevated."
        )

    if trend_info["state"] in {
        "ESCALATING",
        "DETERIORATING",
    }:

        return (
            "Supply-chain risk shows signs of deterioration."
        )

    if transition_info[
        "transition_count"
    ] > 0:

        return (
            "A change in escalation state has been detected."
        )

    if (
        trend_info["operational_status"]
        == "INSUFFICIENT_HISTORY"
    ):

        return (
            "Current trend evidence is insufficient "
            "for a confirmed temporal assessment."
        )

    if risk_info[
        "overall_risk_level"
    ] == "MEDIUM":

        return (
            "Moderate supply-chain disruption exposure "
            "requires monitoring."
        )

    if risk_info[
        "overall_risk_level"
    ] == "LOW":

        return (
            "Current disruption exposure is relatively low."
        )

    return (
        "Available intelligence is insufficient "
        "for a strong decision signal."
    )


def build_evidence(
    risk_info,
    trend_info,
    transition_info,
):
    """Build concise evidence for the decision-maker."""

    evidence = []

    if risk_info[
        "risk_exposure_score"
    ] > 0:

        evidence.append(
            "Risk exposure: "
            f"{risk_info['risk_exposure_score']:.2f}%"
        )

    if risk_info[
        "delayed_percentage"
    ] > 0:

        evidence.append(
            "Delayed shipments: "
            f"{risk_info['delayed_percentage']:.2f}%"
        )

    if risk_info[
        "critical_percentage"
    ] > 0:

        evidence.append(
            "Critical shipments: "
            f"{risk_info['critical_percentage']:.2f}%"
        )

    if risk_info[
        "high_critical_percentage"
    ] > 0:

        evidence.append(
            "High + critical shipments: "
            f"{risk_info['high_critical_percentage']:.2f}%"
        )

    if risk_info[
        "delay_probability"
    ] > 0:

        evidence.append(
            "Average delay probability: "
            f"{risk_info['delay_probability'] * 100:.2f}%"
        )

    if risk_info[
        "expected_delay_days"
    ] > 0:

        evidence.append(
            "Expected delay: "
            f"{risk_info['expected_delay_days']:.3f} days"
        )

    if risk_info[
        "confidence"
    ] > 0:

        evidence.append(
            "Average AI confidence: "
            f"{risk_info['confidence'] * 100:.2f}%"
        )

    if risk_info[
        "intelligence"
    ] > 0:

        evidence.append(
            "Average AI intelligence: "
            f"{risk_info['intelligence'] * 100:.2f}%"
        )

    if risk_info[
        "escalation_score"
    ] > 0:

        evidence.append(
            "Escalation score: "
            f"{risk_info['escalation_score']:.2f}%"
        )

    if risk_info[
        "overall_risk_level"
    ] != "UNKNOWN":

        evidence.append(
            "Overall risk level: "
            f"{risk_info['overall_risk_level']}"
        )

    if trend_info[
        "state"
    ] != "UNKNOWN":

        evidence.append(
            "Trend state: "
            f"{trend_info['state']}"
        )

    if transition_info[
        "transition_count"
    ] > 0:

        evidence.append(
            "State transitions detected: "
            f"{transition_info['transition_count']}"
        )

    if not evidence:

        evidence.append(
            "No sufficient quantitative evidence was available."
        )

    return evidence


def build_decision_signals(
    risk_info,
    trend_info,
    transition_info,
    priority,
):
    """Generate human-readable decision signals."""

    signals = []

    if priority == "CRITICAL":

        signals.append(
            "Immediate manager attention is required."
        )

    elif priority == "HIGH":

        signals.append(
            "Urgent manager review is recommended."
        )

    elif priority == "MEDIUM":

        signals.append(
            "The situation should be monitored closely."
        )

    elif priority == "LOW":

        signals.append(
            "Routine monitoring is currently sufficient."
        )

    else:

        signals.append(
            "Additional evidence is required before "
            "assigning a strong decision priority."
        )

    if risk_info[
        "delayed_percentage"
    ] >= 50:

        signals.append(
            "A large proportion of shipments "
            "are currently exposed to delay."
        )

    if risk_info[
        "critical_percentage"
    ] >= 50:

        signals.append(
            "Critical-risk shipment exposure is significant."
        )

    if risk_info[
        "high_critical_percentage"
    ] >= 75:

        signals.append(
            "High and critical predictions represent "
            "a large majority of the batch."
        )

    if risk_info[
        "escalation_score"
    ] >= 90:

        signals.append(
            "Escalation intensity is at a critical level."
        )

    if trend_info[
        "state"
    ] in {
        "ESCALATING",
        "DETERIORATING",
    }:

        signals.append(
            "Trend intelligence indicates worsening "
            "risk conditions."
        )

    if transition_info[
        "transition_count"
    ] > 0:

        signals.append(
            "Historical state transitions are available "
            "for additional context."
        )

    if (
        trend_info[
            "operational_status"
        ] == "INSUFFICIENT_HISTORY"
    ):

        signals.append(
            "Trend history is insufficient for a "
            "confirmed temporal conclusion."
        )

    return signals


def determine_confidence(
    risk_info,
    trend_info,
    transition_info,
):
    """Determine confidence in the decision-support signal."""

    confidence_values = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "UNKNOWN": 0,
    }

    available = []

    risk_confidence = risk_info[
        "confidence"
    ]

    if risk_confidence > 0:

        if risk_confidence >= 0.75:
            available.append(3)

        elif risk_confidence >= 0.50:
            available.append(2)

        else:
            available.append(1)

    trend_confidence = normalize_text(
        trend_info["confidence"]
    )

    if trend_confidence != "UNKNOWN":

        available.append(
            confidence_values.get(
                trend_confidence,
                0,
            )
        )

    transition_confidence = normalize_text(
        transition_info["confidence"]
    )

    if transition_confidence != "UNKNOWN":

        available.append(
            confidence_values.get(
                transition_confidence,
                0,
            )
        )

    if not available:
        return "LOW"

    average_confidence = (
        sum(available) / len(available)
    )

    if average_confidence >= 2.5:
        return "HIGH"

    if average_confidence >= 1.5:
        return "MEDIUM"

    return "LOW"


def build_report(
    risk_info,
    trend_info,
    transition_info,
):
    """Build the final decision-intelligence report."""

    priority = determine_priority(
        risk_info,
        trend_info,
        transition_info,
    )

    attention_level = determine_attention_level(
        priority
    )

    primary_concern = determine_primary_concern(
        risk_info,
        trend_info,
        transition_info,
    )

    evidence = build_evidence(
        risk_info,
        trend_info,
        transition_info,
    )

    decision_signals = build_decision_signals(
        risk_info,
        trend_info,
        transition_info,
        priority,
    )

    confidence = determine_confidence(
        risk_info,
        trend_info,
        transition_info,
    )

    return {
        "engine": "AI Decision Intelligence Engine",
        "generated_at": datetime.now().isoformat(),
        "decision": {
            "priority": priority,
            "attention_level": attention_level,
            "confidence": confidence,
            "primary_concern": primary_concern,
        },
        "risk_context": risk_info,
        "trend_context": trend_info,
        "transition_context": transition_info,
        "evidence": evidence,
        "decision_signals": decision_signals,
        "operational_recommendation": risk_info[
            "operational_recommendation"
        ],
        "decision_guidance": (
            "Use this intelligence to support manager review. "
            "The engine does not automatically execute business decisions."
        ),
        "operational_safety": {
            "prediction_outputs_modified": "NO",
            "risk_reports_modified": "NO",
            "trend_reports_modified": "NO",
            "state_history_modified": "NO",
            "models_modified": "NO",
            "retraining_triggered": "NO",
            "optimization_modified": "NO",
            "database_modified": "NO",
            "business_decision_executed": "NO",
        },
    }


def save_report(report):
    """Save the decision-intelligence report."""

    try:

        with open(
            OUTPUT_REPORT,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
            )

        return True

    except OSError as error:

        print(
            "   ✗ Failed to save decision-intelligence "
            f"report: {error}"
        )

        return False


def main():

    print("=" * 90)
    print(
        "SUPPLYPRESCRIPT - AI DECISION INTELLIGENCE ENGINE"
    )
    print("=" * 90)

    print(
        "\nLoading risk escalation intelligence..."
    )

    risk_report = load_json_file(
        RISK_ESCALATION_REPORT
    )

    if risk_report is None:

        print(
            "\n✗ Decision intelligence cannot continue "
            "without the risk escalation report."
        )

        return

    print(
        "   ✓ Risk escalation report loaded."
    )

    print(
        "\nLoading trend state intelligence..."
    )

    trend_report = load_json_file(
        TREND_STATE_REPORT
    )

    if trend_report is None:

        print(
            "   ⚠ Trend state report unavailable."
        )

        print(
            "   Continuing with available risk intelligence."
        )

    else:

        print(
            "   ✓ Trend state report loaded."
        )

    print(
        "\nLoading state transition intelligence..."
    )

    transition_report = load_json_file(
        STATE_TRANSITION_REPORT
    )

    if transition_report is None:

        print(
            "   ⚠ State transition report unavailable."
        )

        print(
            "   Continuing with available intelligence."
        )

    else:

        print(
            "   ✓ State transition report loaded."
        )

    print(
        "\nExtracting intelligence..."
    )

    risk_info = extract_risk_information(
        risk_report
    )

    trend_info = extract_trend_information(
        trend_report
    )

    transition_info = extract_transition_information(
        transition_report
    )

    print(
        "   ✓ Intelligence extracted."
    )

    print(
        "\nDetermining decision priority..."
    )

    priority = determine_priority(
        risk_info,
        trend_info,
        transition_info,
    )

    attention_level = determine_attention_level(
        priority
    )

    print(
        f"   Decision priority: {priority}"
    )

    print(
        f"   Attention level: {attention_level}"
    )

    print(
        "\nBuilding decision-intelligence report..."
    )

    report = build_report(
        risk_info,
        trend_info,
        transition_info,
    )

    print(
        "   ✓ Decision-intelligence report built."
    )

    print(
        "\nSaving decision-intelligence report..."
    )

    if not save_report(report):

        print(
            "\n✗ Decision-intelligence engine failed."
        )

        return

    print(
        "   ✓ Decision-intelligence report saved."
    )

    print(
        "\n" + "=" * 90
    )

    print(
        "DECISION INTELLIGENCE"
    )

    print(
        "-" * 90
    )

    print(
        f"Priority: "
        f"{report['decision']['priority']}"
    )

    print(
        f"Attention Level: "
        f"{report['decision']['attention_level']}"
    )

    print(
        f"Confidence: "
        f"{report['decision']['confidence']}"
    )

    print(
        "\nPRIMARY CONCERN"
    )

    print(
        "-" * 90
    )

    print(
        report["decision"]["primary_concern"]
    )

    print(
        "\nEVIDENCE"
    )

    print(
        "-" * 90
    )

    for index, item in enumerate(
        report["evidence"],
        start=1,
    ):

        print(
            f"{index:02d}. {item}"
        )

    print(
        "\nDECISION SIGNALS"
    )

    print(
        "-" * 90
    )

    for index, signal in enumerate(
        report["decision_signals"],
        start=1,
    ):

        print(
            f"{index:02d}. {signal}"
        )

    print(
        "\nOPERATIONAL RECOMMENDATION"
    )

    print(
        "-" * 90
    )

    print(
        report[
            "operational_recommendation"
        ]
    )

    print(
        "\nOPERATIONAL SAFETY"
    )

    print(
        "-" * 90
    )

    for key, value in report[
        "operational_safety"
    ].items():

        print(
            f"{key.replace('_', ' ').title()}: {value}"
        )

    print(
        "\n" + "=" * 90
    )

    print(
        "AI decision intelligence analysis "
        "completed successfully."
    )

    print(
        f"Report saved: {OUTPUT_REPORT}"
    )

    print(
        "=" * 90
    )


if __name__ == "__main__":
    main()