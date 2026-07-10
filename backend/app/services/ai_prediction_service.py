from datetime import date,datetime
from sqlalchemy import func
from app.models.debt import DebtCase
from app.models.case_closure import CaseClosure
from app.models.case_escalation import CaseEscalation
from app.models.ai_prediction import AIModelPrediction
from app import db


def build_case_features(case: DebtCase):
    # Aging weight (non-linear)
    aging_weight = {
        "0-30": 0.15,
        "31-60": 0.35,
        "61-90": 0.65,
        "90+": 0.9
    }.get(case.aging_bucket, 0.5)

    # Escalations (recent escalations matter more)
    escalation_count = CaseEscalation.query.filter_by(case_id=case.id).count()
    escalation_penalty = min(escalation_count * 0.15, 0.6)

    # Historical recovery rate (organization-aware if possible)
    historical_recovery_rate = (
        db.session.query(
            func.avg(CaseClosure.recovered_amount / DebtCase.amount_due)
        )
        .join(DebtCase, DebtCase.id == CaseClosure.case_id)
        .scalar()
        or 0.4
    )

    # Amount risk (larger amount = harder recovery)
    amount_risk = min(case.amount_due / 100000, 1)

    return {
        "aging_weight": aging_weight,
        "escalation_penalty": escalation_penalty,
        "historical_recovery": historical_recovery_rate,
        "amount_risk": amount_risk
    }


def predict_recovery_probability(features: dict) -> float:
    score = (
        0.45 * features["historical_recovery"]
        + 0.30 * (1 - features["aging_weight"])
        - 0.15 * features["escalation_penalty"]
        - 0.10 * features["amount_risk"]
    )

    return round(min(max(score, 0), 1), 2)


def compute_priority_score(case: DebtCase, recovery_probability: float) -> float:
    urgency = {
        "0-30": 0.2,
        "31-60": 0.5,
        "61-90": 0.8,
        "90+": 1.0
    }.get(case.aging_bucket, 0.5)

    financial_impact = min(case.amount_due / 75000, 1)

    priority = (
        0.45 * urgency
        + 0.35 * financial_impact
        + 0.20 * recovery_probability
    )

    return round(min(priority, 1), 2)


def generate_prediction(case: DebtCase):
    features = build_case_features(case)
    recovery_probability = predict_recovery_probability(features)
    priority_score = compute_priority_score(case, recovery_probability)

    prediction = AIModelPrediction.query.filter_by(case_id=case.id).first()
    if not prediction:
        prediction = AIModelPrediction(case_id=case.id)

    prediction.predicted_recovery_probability = recovery_probability
    prediction.priority_score = priority_score
    prediction.model_version = "rule_based_v2"
    prediction.predicted_at = datetime.utcnow()

    db.session.add(prediction)
    db.session.commit()

