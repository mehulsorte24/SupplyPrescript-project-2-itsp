from pathlib import Path
import json
import sys
from datetime import datetime, timezone


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# INPUT FILES
# ============================================================

DRIFT_REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "drift_detection_report.json"
)

DRIFT_TREND_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "drift_trend_report.json"
)

MONITORING_REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "feedback"
    / "model_monitoring_report.json"
)

TRIGGER_REPORT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_trigger.json"
)


# ============================================================
# OUTPUT FILE
# ============================================================

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "retraining"
    / "retraining_decision_report.json"
)


# ============================================================
# DECISION THRESHOLDS
# ============================================================

# A high drift percentage is treated as a strong signal.
HIGH_DRIFT_PERCENTAGE = 40.0

# Moderate drift percentage is treated as a warning.
MODERATE_DRIFT_PERCENTAGE = 20.0

# A worsening trend is an additional retraining signal.
WORSENING_TREND = "WORSENING"

# Model monitoring statuses that indicate model degradation.
UNHEALTHY_STATUSES = {
    "UNHEALTHY",
    "DEGRADED",
    "CRITICAL",
}


# ============================================================
# FILE LOADING
# ============================================================

def load_json_file(
    file_path: Path,
    description: str,
    required: bool = True,
) -> dict:
    """
    Load a JSON file safely.
    """

    print(f"Loading {description}...")

    if not file_path.exists():

        if required:
            raise FileNotFoundError(
                f"{description} not found: {file_path}"
            )

        print(
            f"   ⚠ {description} not found."
        )

        return {}

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except json.JSONDecodeError as error:

        if required:
            raise ValueError(
                f"{description} contains invalid JSON: "
                f"{error}"
            )

        print(
            f"   ⚠ {description} contains invalid JSON."
        )

        return {}

    print(
        f"   ✓ {description} found."
    )

    return data


# ============================================================
# SIGNAL EXTRACTION
# ============================================================

def extract_drift_signals(
    drift_report: dict,
) -> dict:
    """
    Extract the most important signals from the
    latest drift detection report.
    """

    summary = drift_report.get(
        "summary",
        {},
    )

    drift_percentage = float(
        summary.get(
            "drift_percentage",
            0.0,
        )
    )

    drifted_features = int(
        summary.get(
            "drifted_features",
            0,
        )
    )

    overall_status = summary.get(
        "overall_status",
        "UNKNOWN",
    )

    retraining_signal = bool(
        summary.get(
            "retraining_signal",
            False,
        )
    )

    return {
        "drift_percentage": drift_percentage,
        "drifted_features": drifted_features,
        "overall_status": overall_status,
        "retraining_signal": retraining_signal,
    }


def extract_trend_signals(
    trend_report: dict,
) -> dict:
    """
    Extract trend information from the drift history report.
    """

    trend_analysis = trend_report.get(
        "trend_analysis",
        {},
    )

    feature_history = trend_report.get(
        "feature_history",
        {},
    )

    trend = trend_analysis.get(
        "trend",
        "INSUFFICIENT_HISTORY",
    )

    change = trend_analysis.get(
        "change_percentage_points",
        None,
    )

    repeated_features = feature_history.get(
        "repeatedly_drifted_features",
        {},
    )

    return {
        "trend": trend,
        "change_percentage_points": change,
        "repeatedly_drifted_features": (
            repeated_features
        ),
    }


def extract_monitoring_signals(
    monitoring_report: dict,
) -> dict:
    """
    Extract model-health information from the existing
    model monitoring report.
    """

    if not monitoring_report:
        return {
            "status": "UNKNOWN",
            "available": False,
        }

    status = monitoring_report.get(
        "status",
        monitoring_report.get(
            "overall_status",
            "UNKNOWN",
        ),
    )

    return {
        "status": str(status),
        "available": True,
    }


def extract_existing_trigger(
    trigger_report: dict,
) -> dict:
    """
    Read the existing automated retraining trigger result.

    This is treated as supporting evidence only. This engine
    does not overwrite the existing trigger decision.
    """

    if not trigger_report:
        return {
            "available": False,
            "retraining_required": False,
            "status": "UNKNOWN",
        }

    return {
        "available": True,
        "retraining_required": bool(
            trigger_report.get(
                "retraining_required",
                False,
            )
        ),
        "status": trigger_report.get(
            "status",
            "UNKNOWN",
        ),
    }


# ============================================================
# DECISION LOGIC
# ============================================================

def evaluate_retraining_decision(
    drift_signals: dict,
    trend_signals: dict,
    monitoring_signals: dict,
    trigger_signals: dict,
) -> dict:
    """
    Combine drift, trend, model-health, and existing trigger
    signals into one explainable retraining recommendation.
    """

    drift_percentage = drift_signals[
        "drift_percentage"
    ]

    drift_status = drift_signals[
        "overall_status"
    ]

    drift_retraining_signal = drift_signals[
        "retraining_signal"
    ]

    trend = trend_signals[
        "trend"
    ]

    repeated_features = trend_signals[
        "repeatedly_drifted_features"
    ]

    monitoring_status = monitoring_signals[
        "status"
    ]

    existing_trigger = trigger_signals[
        "retraining_required"
    ]

    signals = []

    # --------------------------------------------------------
    # Signal 1 — Existing retraining trigger
    # --------------------------------------------------------

    if existing_trigger:
        signals.append(
            {
                "signal": "EXISTING_TRIGGER",
                "severity": "HIGH",
                "result": "PASS",
                "message": (
                    "Existing automated retraining trigger "
                    "already requires retraining."
                ),
            }
        )

    else:
        signals.append(
            {
                "signal": "EXISTING_TRIGGER",
                "severity": "INFO",
                "result": "PASS",
                "message": (
                    "Existing automated retraining trigger "
                    "does not currently require retraining."
                ),
            }
        )

    # --------------------------------------------------------
    # Signal 2 — Drift detection
    # --------------------------------------------------------

    if drift_retraining_signal:
        signals.append(
            {
                "signal": "DRIFT_SIGNAL",
                "severity": "HIGH",
                "result": "FAIL",
                "message": (
                    "Latest drift detection produced a "
                    "retraining signal."
                ),
            }
        )

    elif drift_percentage >= HIGH_DRIFT_PERCENTAGE:
        signals.append(
            {
                "signal": "DRIFT_LEVEL",
                "severity": "HIGH",
                "result": "FAIL",
                "message": (
                    "High feature drift detected."
                ),
            }
        )

    elif drift_percentage >= MODERATE_DRIFT_PERCENTAGE:
        signals.append(
            {
                "signal": "DRIFT_LEVEL",
                "severity": "MEDIUM",
                "result": "WARNING",
                "message": (
                    "Moderate feature drift detected."
                ),
            }
        )

    else:
        signals.append(
            {
                "signal": "DRIFT_LEVEL",
                "severity": "LOW",
                "result": "PASS",
                "message": (
                    "Current feature drift remains "
                    "below the moderate threshold."
                ),
            }
        )

    # --------------------------------------------------------
    # Signal 3 — Drift trend
    # --------------------------------------------------------

    if trend == WORSENING_TREND:
        signals.append(
            {
                "signal": "DRIFT_TREND",
                "severity": "HIGH",
                "result": "WARNING",
                "message": (
                    "Feature drift is worsening compared "
                    "with the previous observation."
                ),
            }
        )

    elif trend == "IMPROVING":
        signals.append(
            {
                "signal": "DRIFT_TREND",
                "severity": "LOW",
                "result": "PASS",
                "message": (
                    "Feature drift is improving."
                ),
            }
        )

    elif trend == "STABLE":
        signals.append(
            {
                "signal": "DRIFT_TREND",
                "severity": "LOW",
                "result": "PASS",
                "message": (
                    "Feature drift remains stable."
                ),
            }
        )

    else:
        signals.append(
            {
                "signal": "DRIFT_TREND",
                "severity": "INFO",
                "result": "INFO",
                "message": (
                    "Not enough historical observations "
                    "to establish a drift trend."
                ),
            }
        )

    # --------------------------------------------------------
    # Signal 4 — Model monitoring
    # --------------------------------------------------------

    if monitoring_status.upper() in UNHEALTHY_STATUSES:

        signals.append(
            {
                "signal": "MODEL_HEALTH",
                "severity": "HIGH",
                "result": "FAIL",
                "message": (
                    "Model monitoring indicates degraded "
                    "or unhealthy model performance."
                ),
            }
        )

    elif monitoring_status.upper() == "HEALTHY":

        signals.append(
            {
                "signal": "MODEL_HEALTH",
                "severity": "LOW",
                "result": "PASS",
                "message": (
                    "Model monitoring currently reports "
                    "healthy performance."
                ),
            }
        )

    else:

        signals.append(
            {
                "signal": "MODEL_HEALTH",
                "severity": "INFO",
                "result": "INFO",
                "message": (
                    "Model health status could not be "
                    "fully evaluated."
                ),
            }
        )

    # --------------------------------------------------------
    # Final decision
    # --------------------------------------------------------

    high_risk_signals = [
        signal
        for signal in signals
        if signal["severity"] == "HIGH"
        and signal["result"] in {
            "FAIL",
            "WARNING",
        }
    ]

    if existing_trigger:
        decision = "RETRAIN_RECOMMENDED"

        confidence = "HIGH"

        reason = (
            "The existing automated retraining trigger "
            "already requires retraining."
        )

    elif (
        drift_retraining_signal
        or drift_percentage >= HIGH_DRIFT_PERCENTAGE
        or monitoring_status.upper()
        in UNHEALTHY_STATUSES
    ):

        decision = "RETRAIN_RECOMMENDED"

        confidence = "HIGH"

        reason = (
            "Strong evidence of data drift or model "
            "performance degradation was detected."
        )

    elif (
        trend == WORSENING_TREND
        and drift_percentage >= MODERATE_DRIFT_PERCENTAGE
    ):

        decision = "RETRAIN_REVIEW"

        confidence = "MEDIUM"

        reason = (
            "Drift is worsening and has reached a "
            "moderate level. Model performance should "
            "be evaluated before retraining."
        )

    elif repeated_features:

        decision = "RETRAIN_REVIEW"

        confidence = "MEDIUM"

        reason = (
            "Repeated feature drift has been observed "
            "historically. Investigate the affected "
            "features and evaluate model performance."
        )

    else:

        decision = "NO_RETRAINING_REQUIRED"

        confidence = "HIGH"

        reason = (
            "Current drift, drift trend, and model health "
            "do not provide sufficient evidence for retraining."
        )

    return {
        "decision": decision,
        "confidence": confidence,
        "reason": reason,
        "high_risk_signal_count": len(
            high_risk_signals
        ),
        "signals": signals,
    }


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(
    drift_report: dict,
    trend_report: dict,
    monitoring_report: dict,
    trigger_report: dict,
) -> dict:
    """
    Generate the complete retraining decision report.
    """

    drift_signals = extract_drift_signals(
        drift_report
    )

    trend_signals = extract_trend_signals(
        trend_report
    )

    monitoring_signals = extract_monitoring_signals(
        monitoring_report
    )

    trigger_signals = extract_existing_trigger(
        trigger_report
    )

    decision = evaluate_retraining_decision(
        drift_signals=drift_signals,
        trend_signals=trend_signals,
        monitoring_signals=monitoring_signals,
        trigger_signals=trigger_signals,
    )

    return {
        "engine": (
            "AI Drift-Aware Retraining Decision Engine"
        ),
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "model_version": drift_report.get(
            "model_version",
            "unknown",
        ),
        "decision": decision,
        "evidence": {
            "drift": drift_signals,
            "trend": trend_signals,
            "model_monitoring": monitoring_signals,
            "existing_retraining_trigger": (
                trigger_signals
            ),
        },
        "decision_policy": {
            "high_drift_percentage": (
                HIGH_DRIFT_PERCENTAGE
            ),
            "moderate_drift_percentage": (
                MODERATE_DRIFT_PERCENTAGE
            ),
            "worsening_trend_requires_review": True,
            "unhealthy_model_statuses": sorted(
                UNHEALTHY_STATUSES
            ),
        },
        "operational_scope": (
            "This engine recommends or reviews retraining. "
            "It does not train, replace, promote, or rollback "
            "model artifacts."
        ),
    }


def save_report(report: dict) -> None:
    """
    Save the retraining decision report.
    """

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
            report,
            file,
            indent=4,
        )

    print(
        "\n✓ Retraining decision report saved:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )


# ============================================================
# MAIN ENGINE
# ============================================================

def run_retraining_decision_engine() -> dict:
    """
    Execute the complete drift-aware retraining decision workflow.
    """

    drift_report = load_json_file(
        DRIFT_REPORT_FILE,
        "drift detection report",
    )

    trend_report = load_json_file(
        DRIFT_TREND_FILE,
        "drift trend report",
    )

    monitoring_report = load_json_file(
        MONITORING_REPORT_FILE,
        "model monitoring report",
        required=False,
    )

    trigger_report = load_json_file(
        TRIGGER_REPORT_FILE,
        "existing retraining trigger report",
        required=False,
    )

    print(
        "\nEvaluating retraining signals..."
    )

    report = generate_report(
        drift_report=drift_report,
        trend_report=trend_report,
        monitoring_report=monitoring_report,
        trigger_report=trigger_report,
    )

    decision = report["decision"]

    evidence = report["evidence"]

    drift = evidence["drift"]

    trend = evidence["trend"]

    monitoring = evidence["model_monitoring"]

    trigger = evidence[
        "existing_retraining_trigger"
    ]

    print("\n" + "=" * 90)

    print(
        "SUPPLYPRESCRIPT - AI DRIFT-AWARE "
        "RETRAINING DECISION ENGINE"
    )

    print("=" * 90)

    print(
        f"\nModel Version: "
        f"{report['model_version']}"
    )

    print(
        f"Current Drift: "
        f"{drift['drift_percentage']:.2f}%"
    )

    print(
        f"Drift Status: "
        f"{drift['overall_status']}"
    )

    print(
        f"Drift Trend: "
        f"{trend['trend']}"
    )

    print(
        f"Model Health: "
        f"{monitoring['status']}"
    )

    print(
        f"Existing Retraining Trigger: "
        f"{trigger['retraining_required']}"
    )

    print(
        "\nFinal Retraining Decision:"
    )

    print(
        f"   {decision['decision']}"
    )

    print(
        f"Decision Confidence: "
        f"{decision['confidence']}"
    )

    print(
        f"High-Risk Signals: "
        f"{decision['high_risk_signal_count']}"
    )

    print(
        "\nDecision Reason:"
    )

    print(
        f"   {decision['reason']}"
    )

    print(
        "\nSignal Evaluation:"
    )

    for signal in decision["signals"]:

        print(
            f"   {signal['signal']}: "
            f"{signal['result']} "
            f"- {signal['message']}"
        )

    print(
        "\nOperational Scope:"
    )

    print(
        "   Recommendation only — "
        "no model artifacts modified."
    )

    print("\n" + "=" * 90)

    save_report(report)

    print(
        "\nAI DRIFT-AWARE RETRAINING DECISION ENGINE "
        "COMPLETED"
    )

    return report


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        run_retraining_decision_engine()

    except FileNotFoundError as error:

        print("\n✗ File Error:")
        print(f"  {error}")

        sys.exit(1)

    except ValueError as error:

        print("\n✗ Data Error:")
        print(f"  {error}")

        sys.exit(1)

    except Exception as error:

        print("\n✗ Unexpected Error:")
        print(f"  {error}")

        sys.exit(1)