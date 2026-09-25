import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path.cwd()
PREDICTION_DIR = BASE_DIR / "ai_engine" / "prediction"

DECISION_INTELLIGENCE_REPORT = (
    PREDICTION_DIR / "decision_intelligence_report.json"
)

OUTPUT_REPORT = (
    PREDICTION_DIR / "action_recommendation_report.json"
)


def load_json_file(file_path):
    """Load a JSON file safely."""

    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return None

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        print(
            f"   ✗ Invalid JSON in {file_path.name}: {error}"
        )
        return None

    except OSError as error:
        print(
            f"   ✗ Failed to read {file_path.name}: {error}"
        )
        return None


def safe_float(value, default=0.0):
    """Convert a value to float safely."""

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def normalize_text(value, default="UNKNOWN"):
    """Convert a value to normalized uppercase text."""

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text.upper()


def extract_intelligence(report):
    """Extract decision and risk intelligence."""

    if not isinstance(report, dict):
        return {
            "priority": "UNKNOWN",
            "attention_level": "UNKNOWN",
            "confidence": "UNKNOWN",
            "primary_concern": "UNKNOWN",
            "risk_exposure": 0.0,
            "delayed_percentage": 0.0,
            "critical_percentage": 0.0,
            "high_critical_percentage": 0.0,
            "delay_probability": 0.0,
            "expected_delay_days": 0.0,
            "overall_risk_level": "UNKNOWN",
            "escalation_score": 0.0,
            "escalation_level": "UNKNOWN",
            "recommended_action": "UNKNOWN",
            "operational_recommendation": "UNKNOWN",
            "trend_state": "UNKNOWN",
            "trend_status": "UNKNOWN",
        }

    decision = report.get(
        "decision",
        {},
    )

    if not isinstance(decision, dict):
        decision = {}

    risk_context = report.get(
        "risk_context",
        {},
    )

    if not isinstance(risk_context, dict):
        risk_context = {}

    trend_context = report.get(
        "trend_context",
        {},
    )

    if not isinstance(trend_context, dict):
        trend_context = {}

    return {
        "priority": normalize_text(
            decision.get(
                "priority",
                "UNKNOWN",
            )
        ),
        "attention_level": normalize_text(
            decision.get(
                "attention_level",
                "UNKNOWN",
            )
        ),
        "confidence": normalize_text(
            decision.get(
                "confidence",
                "UNKNOWN",
            )
        ),
        "primary_concern": decision.get(
            "primary_concern",
            "UNKNOWN",
        ),
        "risk_exposure": safe_float(
            risk_context.get(
                "risk_exposure_score",
                0.0,
            )
        ),
        "delayed_percentage": safe_float(
            risk_context.get(
                "delayed_percentage",
                0.0,
            )
        ),
        "critical_percentage": safe_float(
            risk_context.get(
                "critical_percentage",
                0.0,
            )
        ),
        "high_critical_percentage": safe_float(
            risk_context.get(
                "high_critical_percentage",
                0.0,
            )
        ),
        "delay_probability": safe_float(
            risk_context.get(
                "delay_probability",
                0.0,
            )
        ),
        "expected_delay_days": safe_float(
            risk_context.get(
                "expected_delay_days",
                0.0,
            )
        ),
        "overall_risk_level": normalize_text(
            risk_context.get(
                "overall_risk_level",
                "UNKNOWN",
            )
        ),
        "escalation_score": safe_float(
            risk_context.get(
                "escalation_score",
                0.0,
            )
        ),
        "escalation_level": normalize_text(
            risk_context.get(
                "escalation_level",
                "UNKNOWN",
            )
        ),
        "recommended_action": normalize_text(
            risk_context.get(
                "recommended_action",
                "UNKNOWN",
            )
        ),
        "operational_recommendation": risk_context.get(
            "operational_recommendation",
            "UNKNOWN",
        ),
        "trend_state": normalize_text(
            trend_context.get(
                "state",
                "UNKNOWN",
            )
        ),
        "trend_status": normalize_text(
            trend_context.get(
                "operational_status",
                "UNKNOWN",
            )
        ),
    }


def determine_action_urgency(intelligence):
    """Determine how urgently mitigation options should be reviewed."""

    priority = intelligence["priority"]

    if priority == "CRITICAL":
        return "IMMEDIATE"

    if priority == "HIGH":
        return "URGENT"

    if priority == "MEDIUM":
        return "MONITOR"

    if priority == "LOW":
        return "ROUTINE"

    return "INSUFFICIENT_EVIDENCE"


def build_action(
    action_id,
    action_name,
    category,
    rationale,
    trigger,
    expected_effect,
    trade_off,
    urgency,
):
    """Create one structured mitigation option."""

    return {
        "action_id": action_id,
        "action_name": action_name,
        "category": category,
        "rationale": rationale,
        "trigger": trigger,
        "expected_effect": expected_effect,
        "trade_off": trade_off,
        "urgency": urgency,
        "execution_status": "MANAGER_REVIEW_REQUIRED",
    }


def generate_actions(intelligence):
    """Generate candidate mitigation actions."""

    actions = []

    urgency = determine_action_urgency(
        intelligence
    )

    risk_level = intelligence[
        "overall_risk_level"
    ]

    delay_probability = intelligence[
        "delay_probability"
    ]

    expected_delay = intelligence[
        "expected_delay_days"
    ]

    delayed_percentage = intelligence[
        "delayed_percentage"
    ]

    critical_percentage = intelligence[
        "critical_percentage"
    ]

    risk_exposure = intelligence[
        "risk_exposure"
    ]

    if (
        risk_level == "CRITICAL"
        or risk_exposure >= 75
        or critical_percentage >= 50
    ):
        actions.append(
            build_action(
                "ACT-001",
                "Expedite transportation",
                "TRANSPORT_EXPEDITION",
                (
                    "High disruption exposure indicates that "
                    "faster transportation may reduce the impact "
                    "of shipment delays."
                ),
                (
                    f"Risk exposure is {risk_exposure:.2f}% "
                    f"and critical shipments represent "
                    f"{critical_percentage:.2f}% of the batch."
                ),
                (
                    "Potentially reduce transit time and limit "
                    "the operational impact of delayed shipments."
                ),
                (
                    "Potentially higher transportation cost and "
                    "limited availability of expedited capacity."
                ),
                urgency,
            )
        )

    if (
        risk_level in {
            "CRITICAL",
            "HIGH",
        }
        or delay_probability >= 0.50
    ):
        actions.append(
            build_action(
                "ACT-002",
                "Evaluate alternate supplier",
                "SUPPLIER_ALTERNATIVE",
                (
                    "A high probability of disruption may justify "
                    "evaluating another qualified supplier."
                ),
                (
                    f"Predicted delay probability is "
                    f"{delay_probability * 100:.2f}%."
                ),
                (
                    "Potentially reduce dependency on the "
                    "currently exposed supply route or supplier."
                ),
                (
                    "Alternative suppliers may have higher cost, "
                    "qualification requirements, or lower capacity."
                ),
                urgency,
            )
        )

    if (
        expected_delay >= 2
        or delayed_percentage >= 50
    ):
        actions.append(
            build_action(
                "ACT-003",
                "Increase inventory buffer",
                "INVENTORY_BUFFER",
                (
                    "Expected disruption duration may justify "
                    "temporarily increasing safety stock."
                ),
                (
                    f"Expected delay is "
                    f"{expected_delay:.3f} days and "
                    f"{delayed_percentage:.2f}% of predictions "
                    f"are delayed."
                ),
                (
                    "Provide additional inventory coverage while "
                    "the disruption is being resolved."
                ),
                (
                    "Higher inventory holding cost and possible "
                    "working-capital impact."
                ),
                urgency,
            )
        )

    if (
        critical_percentage >= 25
        or risk_level in {
            "CRITICAL",
            "HIGH",
        }
    ):
        actions.append(
            build_action(
                "ACT-004",
                "Prioritize critical shipments",
                "PRIORITY_REALLOCATION",
                (
                    "Critical-risk shipments should be reviewed "
                    "and prioritized according to business impact."
                ),
                (
                    f"Critical shipments represent "
                    f"{critical_percentage:.2f}% of the batch."
                ),
                (
                    "Focus limited logistics capacity on shipments "
                    "with the highest operational exposure."
                ),
                (
                    "Prioritization may delay lower-priority "
                    "shipments and requires business judgment."
                ),
                urgency,
            )
        )

    if (
        intelligence["trend_status"]
        == "INSUFFICIENT_HISTORY"
    ):
        actions.append(
            build_action(
                "ACT-005",
                "Increase monitoring frequency",
                "MONITORING",
                (
                    "Current risk is significant, but historical "
                    "trend evidence is insufficient for a confirmed "
                    "temporal assessment."
                ),
                (
                    "Only limited historical trend information "
                    "is currently available."
                ),
                (
                    "Provide additional observations that can "
                    "strengthen future trend assessment."
                ),
                (
                    "Monitoring alone does not directly reduce "
                    "the current disruption risk."
                ),
                "CONTINUOUS",
            )
        )

    if not actions:
        actions.append(
            build_action(
                "ACT-000",
                "Continue routine monitoring",
                "MONITORING",
                (
                    "Available intelligence does not currently "
                    "justify a specific mitigation action."
                ),
                (
                    "No strong risk trigger was identified."
                ),
                (
                    "Maintain visibility while collecting "
                    "additional operational evidence."
                ),
                (
                    "A passive approach may be insufficient "
                    "if risk conditions deteriorate."
                ),
                "ROUTINE",
            )
        )

    return actions


def rank_actions(actions, intelligence):
    """Rank actions by relevance to the current risk."""

    ranked = []

    risk_level = intelligence[
        "overall_risk_level"
    ]

    critical_percentage = intelligence[
        "critical_percentage"
    ]

    expected_delay = intelligence[
        "expected_delay_days"
    ]

    for action in actions:

        action_id = action[
            "action_id"
        ]

        score = 0
        reasons = []

        if risk_level == "CRITICAL":
            score += 30

        elif risk_level == "HIGH":
            score += 20

        elif risk_level == "MEDIUM":
            score += 10

        if critical_percentage >= 50:

            if action_id in {
                "ACT-001",
                "ACT-004",
            }:
                score += 25

                reasons.append(
                    "Critical shipment exposure is significant."
                )

        if expected_delay >= 3:

            if action_id in {
                "ACT-001",
                "ACT-003",
            }:
                score += 20

                reasons.append(
                    "Expected delay duration is substantial."
                )

        if action_id == "ACT-002":

            if intelligence[
                "delay_probability"
            ] >= 0.70:
                score += 20

                reasons.append(
                    "Delay probability is highly elevated."
                )

        if action_id == "ACT-005":

            if intelligence[
                "trend_status"
            ] == "INSUFFICIENT_HISTORY":
                score += 15

                reasons.append(
                    "Additional history is needed for stronger "
                    "trend intelligence."
                )

        if not reasons:
            reasons.append(
                "Action is relevant to the current risk profile."
            )

        ranked.append(
            {
                "action_id": action_id,
                "action_name": action[
                    "action_name"
                ],
                "relevance_score": score,
                "ranking_reasons": reasons,
            }
        )

    ranked.sort(
        key=lambda item: (
            item["relevance_score"],
            item["action_id"],
        ),
        reverse=True,
    )

    for index, item in enumerate(
        ranked,
        start=1,
    ):
        item["rank"] = index

    return ranked


def build_recommendation_summary(
    actions,
    ranked_actions,
    intelligence,
):
    """Build a concise manager-facing recommendation summary."""

    if not ranked_actions:
        return (
            "No actionable mitigation options were generated."
        )

    top_action = ranked_actions[0]

    return (
        f"{len(actions)} mitigation options were generated. "
        f"The highest-relevance option is "
        f"'{top_action['action_name']}'. "
        f"Manager review is required before execution."
    )


def build_report(intelligence):
    """Build the complete action recommendation report."""

    urgency = determine_action_urgency(
        intelligence
    )

    actions = generate_actions(
        intelligence
    )

    ranked_actions = rank_actions(
        actions,
        intelligence,
    )

    recommendation_summary = (
        build_recommendation_summary(
            actions,
            ranked_actions,
            intelligence,
        )
    )

    return {
        "engine": "AI Action Recommendation Engine",
        "generated_at": datetime.now().isoformat(),
        "source": {
            "decision_intelligence_report": str(
                DECISION_INTELLIGENCE_REPORT
            ),
        },
        "decision_context": {
            "priority": intelligence[
                "priority"
            ],
            "attention_level": intelligence[
                "attention_level"
            ],
            "confidence": intelligence[
                "confidence"
            ],
            "overall_risk_level": intelligence[
                "overall_risk_level"
            ],
            "risk_exposure": intelligence[
                "risk_exposure"
            ],
            "delayed_percentage": intelligence[
                "delayed_percentage"
            ],
            "critical_percentage": intelligence[
                "critical_percentage"
            ],
            "delay_probability": intelligence[
                "delay_probability"
            ],
            "expected_delay_days": intelligence[
                "expected_delay_days"
            ],
            "escalation_score": intelligence[
                "escalation_score"
            ],
            "trend_state": intelligence[
                "trend_state"
            ],
            "trend_status": intelligence[
                "trend_status"
            ],
        },
        "recommendation": {
            "urgency": urgency,
            "option_count": len(actions),
            "summary": recommendation_summary,
            "ranked_actions": ranked_actions,
            "candidate_actions": actions,
        },
        "manager_guidance": (
            "These are AI-generated candidate actions for "
            "manager evaluation. The engine does not execute "
            "business decisions, modify shipments, change "
            "suppliers, purchase capacity, or alter inventory."
        ),
        "operational_safety": {
            "prediction_outputs_modified": "NO",
            "risk_reports_modified": "NO",
            "decision_intelligence_modified": "NO",
            "models_modified": "NO",
            "retraining_triggered": "NO",
            "optimization_executed": "NO",
            "shipment_modified": "NO",
            "supplier_modified": "NO",
            "inventory_modified": "NO",
            "database_modified": "NO",
            "business_decision_executed": "NO",
        },
    }


def save_report(report):
    """Save the recommendation report."""

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
            "   ✗ Failed to save recommendation report: "
            f"{error}"
        )

        return False


def main():

    print("=" * 90)

    print(
        "SUPPLYPRESCRIPT - AI ACTION RECOMMENDATION ENGINE"
    )

    print("=" * 90)

    print(
        "\nLoading decision intelligence..."
    )

    decision_report = load_json_file(
        DECISION_INTELLIGENCE_REPORT
    )

    if decision_report is None:

        print(
            "\n✗ Action recommendation engine cannot continue."
        )

        print(
            "  Run decision_intelligence.py first."
        )

        return

    print(
        "   ✓ Decision intelligence loaded."
    )

    print(
        "\nExtracting decision context..."
    )

    intelligence = extract_intelligence(
        decision_report
    )

    print(
        "   ✓ Decision context extracted."
    )

    print(
        "\nGenerating mitigation options..."
    )

    actions = generate_actions(
        intelligence
    )

    print(
        f"   ✓ {len(actions)} candidate actions generated."
    )

    print(
        "\nRanking mitigation options..."
    )

    ranked_actions = rank_actions(
        actions,
        intelligence,
    )

    print(
        "   ✓ Actions ranked by relevance."
    )

    print(
        "\nBuilding recommendation report..."
    )

    report = build_report(
        intelligence
    )

    print(
        "   ✓ Recommendation report built."
    )

    print(
        "\nSaving recommendation report..."
    )

    if not save_report(report):

        print(
            "\n✗ Action recommendation engine failed."
        )

        return

    print(
        "   ✓ Recommendation report saved."
    )

    print(
        "\n" + "=" * 90
    )

    print(
        "ACTION RECOMMENDATION INTELLIGENCE"
    )

    print(
        "-" * 90
    )

    print(
        f"Risk Level: "
        f"{intelligence['overall_risk_level']}"
    )

    print(
        f"Risk Exposure: "
        f"{intelligence['risk_exposure']:.2f}%"
    )

    print(
        f"Delay Probability: "
        f"{intelligence['delay_probability'] * 100:.2f}%"
    )

    print(
        f"Expected Delay: "
        f"{intelligence['expected_delay_days']:.3f} days"
    )

    print(
        f"Recommendation Urgency: "
        f"{report['recommendation']['urgency']}"
    )

    print(
        f"Candidate Actions: "
        f"{report['recommendation']['option_count']}"
    )

    print(
        "\nRANKED MITIGATION OPTIONS"
    )

    print(
        "-" * 90
    )

    for action in ranked_actions:

        print(
            f"{action['rank']:02d}. "
            f"{action['action_name']} "
            f"| Score: "
            f"{action['relevance_score']}"
        )

        for reason in action[
            "ranking_reasons"
        ]:

            print(
                f"    Reason: {reason}"
            )

    print(
        "\nMANAGER GUIDANCE"
    )

    print(
        "-" * 90
    )

    print(
        report["manager_guidance"]
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
        "AI action recommendation analysis "
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