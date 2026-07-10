# routes/enterprise.py
from flask import Blueprint, request, jsonify, session, abort,current_app
from datetime import datetime, date
import pandas as pd

from app import db
from app.models.debt import DebtCase
from app.models.case_assignment import CaseAssignment
from app.models.case_escalation import CaseEscalation
from app.models.case_closure import CaseClosure
from app.models.sla import CaseSLATracking, SLADefinition
from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.services.ai_prediction_service import generate_prediction
from .analytics_chart import generate_aging_chart, generate_priority_chart

enterprise_bp = Blueprint("enterprise", __name__)

# ---------- ACCESS GUARD ----------
def enterprise_only():
    if session.get("role") != "ENTERPRISE":
        abort(403)

# ---------- DASHBOARD ----------
@enterprise_bp.route("/dashboard")
def enterprise_dashboard():
    enterprise_only()
    return "Enterprise Dashboard"

# ---------- ANALYTICS ----------
@enterprise_bp.route("/analytics/charts", methods=["GET"])
def analytics_charts():
    enterprise_only()
    cases = DebtCase.query.filter_by(
    enterprise_id=session["organization_id"]
).all()
    return jsonify({
        "aging_chart": generate_aging_chart(cases),
        "priority_chart": generate_priority_chart(cases)
    })

# ---------- OVERVIEW ----------
@enterprise_bp.route("/overview", methods=["GET"])
def enterprise_overview():
    enterprise_only()

    return jsonify({
        "total_overdue": DebtCase.query.filter_by(enterprise_id=session["organization_id"]).count(),
        "in_progress": DebtCase.query.filter(
            DebtCase.status.in_(["NEW", "PENDING"]),DebtCase.enterprise_id==session["organization_id"]
        ).count(),
        "escalated": DebtCase.query.filter_by(status="ESCALATED",enterprise_id=session["organization_id"]).count(),
        "closed": DebtCase.query.filter(
            DebtCase.status.in_(["Collected", "CLOSED"]),DebtCase.enterprise_id==session["organization_id"]
        ).count()
    })

# ---------- HELPERS ----------
def calculate_aging(due_date):
    if not due_date:
        return None, None

    if isinstance(due_date, str):
        try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return None, None

    days = (date.today() - due_date).days

    if days <= 30:
        return days, "0-30"
    if days <= 60:
        return days, "31-60"
    if days <= 90:
        return days, "61-90"
    return days, "90+"

# ---------- BULK UPLOAD ----------
@enterprise_bp.route("/cases/upload", methods=["POST"])
def upload_cases():
    enterprise_only()

    file = request.files["file"]
    df = pd.read_csv(file) if file.filename.endswith(".csv") else pd.read_excel(file)

    created = 0

    for _, row in df.iterrows():
        if DebtCase.query.filter_by(tracking_number=row["tracking_number"]).first():
            continue

        aging_days, aging_bucket = calculate_aging(row.get("due_date"))

        case = DebtCase(
            tracking_number=row["tracking_number"],
            customer_name=row["customer_name"],
            amount_due=row["amount_due"],
            due_date=row.get("due_date"),
            aging_days=aging_days,
            aging_bucket=aging_bucket,
            status="NEW",
            enterprise_id=session["organization_id"]
        )

        db.session.add(case)
        db.session.flush()
        generate_prediction(case)
        created += 1

    db.session.add(AuditLog(
        entity_type="DebtCase",
        action="BULK_UPLOAD",
        performed_by=session.get("user_id"),
        performed_at=datetime.utcnow(),
        audit_metadata={"rows_created": created}
    ))

    db.session.commit()
    return jsonify({"created": created})

# ---------- LIST CASES ----------
@enterprise_bp.route("/cases", methods=["GET"])
def list_cases():
    enterprise_only()
    cases = DebtCase.query.filter_by(
    enterprise_id=session["organization_id"]
).all()
    
    return jsonify([{
        "id": c.id,
        "tracking_number": c.tracking_number,
        "customer_name": c.customer_name,
        "amount_due": c.amount_due,
        "aging_bucket": c.aging_bucket,
        "status": c.status,
        "recovery_probability": c.prediction.predicted_recovery_probability if c.prediction else None,
        "priority_score": c.prediction.priority_score if c.prediction else None,
        # ✅ SAFE closure access
    "recovered_amount": (
        c.closure.recovered_amount
        if c.closure else None
    )
    } for c in cases])

# ---------- ASSIGN ----------
@enterprise_bp.route("/assign", methods=["POST"])
def assign_cases():
    if session.get("role") != "ENTERPRISE":
        abort(403)

    data = request.get_json(silent=True) or {}
    case_ids = data.get("case_ids")
    dca_id = data.get("dca_id")

    if not case_ids or not dca_id:
        return jsonify({"error": "case_ids and dca_id are required"}), 400

    sla = SLADefinition.query.filter_by(active=True).first()
    assigned_by = session.get("user_id")

    for case_id in case_ids:
        existing_assignment = CaseAssignment.query.filter_by(
            case_id=case_id,
            unassigned_at=None
        ).first()

        if existing_assignment:
            continue

        # ✅ CREATE ASSIGNMENT
        db.session.add(CaseAssignment(
            case_id=case_id,
            dca_id=dca_id,
            assigned_by=assigned_by,
            assigned_at=datetime.utcnow()
        ))

        # ✅ UPDATE CASE STATUS (CRITICAL FIX)
        case = DebtCase.query.get(case_id)
        if case and case.status == "NEW":
            case.status = "PENDING"
            db.session.add(case)

        # ✅ START SLA
        if sla:
            existing_sla = CaseSLATracking.query.filter_by(
                case_id=case_id,
                status="RUNNING"
            ).first()

            if not existing_sla:
                db.session.add(CaseSLATracking(
                    case_id=case_id,
                    sla_definition_id=sla.id,
                    started_at=datetime.utcnow(),
                    status="RUNNING"
                ))

    db.session.add(AuditLog(
        entity_type="CaseAssignment",
        action="BULK_ASSIGN",
        performed_by=assigned_by,
        performed_at=datetime.utcnow()
    ))

    db.session.commit()
    return jsonify({"status": "assigned"})

# ---------- SLA ----------
@enterprise_bp.route("/sla", methods=["GET"])
def sla_monitor():
    enterprise_only()
    slas = CaseSLATracking.query.all()

    return jsonify([{
        "case_id": s.case_id,
        "status": s.status,
        "started_at": s.started_at,
        "breached_at": s.breached_at
    } for s in slas])

# ---------- CLOSE CASE ----------
# ---------- CLOSE / DISPUTE CASE ----------
@enterprise_bp.route("/cases/<int:id>/close", methods=["POST"])
def close_case(id):
    enterprise_only()
    data = request.json or {}

    closure_reason = data.get("reason")
    recovered_amount = data.get("amount", 0)

    if not closure_reason:
        return jsonify({"error": "reason is required"}), 400

    case = DebtCase.query.get_or_404(id)

    if case.status == "CLOSED":
        return jsonify({"error": "Case already closed"}), 400

    is_dispute = closure_reason == "DISPUTE"

    if is_dispute:
        case.status = "DISPUTED"

        sla = CaseSLATracking.query.filter_by(
            case_id=id,
            status="RUNNING"
        ).first()

        if sla:
            sla.status = "PAUSED"
            sla.paused_at = datetime.utcnow()

        audit_action = "DISPUTE"

    else:
        existing_closure = CaseClosure.query.filter_by(case_id=id).first()
        if existing_closure:
            return jsonify({"error": "Closure already exists for this case"}), 400

        db.session.add(CaseClosure(
            case_id=id,
            recovered_amount=recovered_amount,
            closure_reason=closure_reason,
            closed_by=session["user_id"],
            closed_at=datetime.utcnow()
        ))

        case.status = "CLOSED"
        case.closed_at = datetime.utcnow()

        sla = CaseSLATracking.query.filter_by(
            case_id=id,
            status="RUNNING"
        ).first()

        if sla:
            sla.status = "COMPLETED"
            sla.completed_at = datetime.utcnow()

        # audit action reflects business outcome
        audit_action = closure_reason

    db.session.add(AuditLog(
        entity_type="DebtCase",
        entity_id=id,
        action=audit_action,
        performed_by=session.get("user_id"),
        performed_at=datetime.utcnow(),
    ))

    db.session.commit()

    return jsonify({
        "status": "closed"
    })



@enterprise_bp.route("/dcas", methods=["GET"])
def list_dcas():
    enterprise_only()

    dcas = Organization.query.filter_by(type="DCA").all()

    return jsonify([
        {
            "id": d.id,
            "name": d.name
        }
        for d in dcas
    ])

@enterprise_bp.route("/sla/status", methods=["GET"])
def sla_status_overview():
    enterprise_only()

    enterprise_id = session["organization_id"]

    slas = (
        CaseSLATracking.query
        .join(DebtCase, DebtCase.id == CaseSLATracking.case_id)
        .filter(DebtCase.enterprise_id == enterprise_id)
        .all()
    )

    return jsonify([{
        "case_id": s.case_id,
        "status": s.status,
        "started_at": s.started_at,
        "breached_at": s.breached_at,
        "sla_name": s.sla_definition.name,
        "max_resolution_hours": s.sla_definition.max_resolution_hours
    } for s in slas])


@enterprise_bp.route("/escalations/pending", methods=["GET"])
def list_pending_escalations():
    enterprise_only()

    enterprise_id = session["organization_id"]

    escalations = (
        CaseEscalation.query
        .join(DebtCase, DebtCase.id == CaseEscalation.case_id)
        .filter(
            DebtCase.enterprise_id == enterprise_id,
            CaseEscalation.status == "PENDING"
        )
        .all()
    )

    return jsonify([
        {
            "case_id": e.case_id,
            "status": e.status,
            "reason": e.reason,
            "requested_at": e.requested_at,
            "requested_by": e.requested_by
        }
        for e in escalations
    ])


@enterprise_bp.route("/escalations/approve", methods=["POST"])
def approve_escalation():
    enterprise_only()

    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")

    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    escalation = CaseEscalation.query.filter_by(
        case_id=case_id,
        status="PENDING"
    ).first_or_404()

    # ---- APPROVE ESCALATION ----
    escalation.status = "APPROVED"
    escalation.reviewed_at = datetime.utcnow()
    escalation.reviewed_by = session["user_id"]

    # ---- UPDATE CASE ----
    case = DebtCase.query.get_or_404(case_id)
    case.status = "ESCALATED"

    # ---- UNASSIGN DCA ----
    assignment = CaseAssignment.query.filter_by(
        case_id=case_id,
        unassigned_at=None
    ).first()

    if assignment:
        assignment.unassigned_at = datetime.utcnow()

    # ---- COMPLETE SLA ----
    sla = CaseSLATracking.query.filter_by(
        case_id=case_id,
        status="RUNNING"
    ).first()

    if sla:
        sla.status = "COMPLETED"
        sla.breached_at = datetime.utcnow()

    # ---- AUDIT LOG ----
    db.session.add(AuditLog(
        entity_type="CaseEscalation",
        entity_id=str(case_id),
        action="ESCALATION_APPROVED",
        performed_by=session["user_id"],
        performed_at=datetime.utcnow()
    ))

    db.session.commit()
    return jsonify({"status": "approved"})


@enterprise_bp.route("/escalations/reject", methods=["POST"])
def reject_escalation():
    enterprise_only()

    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")

    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    escalation = CaseEscalation.query.filter_by(
        case_id=case_id,
        status="PENDING"
    ).first_or_404()

    # ---- REJECT ESCALATION ----
    escalation.status = "REJECTED"

    # ---- RESET CASE STATUS (CRITICAL FIX) ----
    case = DebtCase.query.get_or_404(case_id)

    if case.status != "CLOSED":
        case.status = "PENDING"   # 👈 BACK TO DCA FLOW

    # ---- ENSURE CASE IS STILL ASSIGNED ----
    assignment = CaseAssignment.query.filter_by(
        case_id=case_id,
        unassigned_at=None
    ).first()

    if not assignment:
        # this should rarely happen, but be safe
        assignment = CaseAssignment(
            case_id=case_id,
            dca_id=escalation.requested_by_org_id,  # or derive properly
            assigned_at=datetime.utcnow()
        )
        db.session.add(assignment)

    # ---- RESTART SLA (ONLY IF NOT CLOSED) ----
    if case.status != "CLOSED":
        existing_sla = CaseSLATracking.query.filter_by(
            case_id=case_id,
            status="RUNNING"
        ).first()

        if not existing_sla:
            sla_def = SLADefinition.query.filter_by(active=True).first()
            if sla_def:
                db.session.add(CaseSLATracking(
                    case_id=case_id,
                    sla_definition_id=sla_def.id,
                    started_at=datetime.utcnow(),
                    status="RUNNING"
                ))

    # ---- AUDIT LOG ----
    db.session.add(AuditLog(
        entity_type="CaseEscalation",
        entity_id=str(case_id),
        action="ESCALATION_REJECTED",
        performed_by=session["user_id"],
        performed_at=datetime.utcnow()
    ))

    db.session.commit()
    return jsonify({"status": "rejected"})