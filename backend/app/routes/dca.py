from flask import Blueprint, session, jsonify, abort,request
from app.models.case_assignment import CaseAssignment
from app.models.debt import DebtCase
from app.models.user import User
from app.models.audit_log import AuditLog
from datetime import datetime
from app import db
from app.models.case_activity import CaseActivityLog
from app.models.case_escalation import CaseEscalation
from app.models.sla import CaseSLATracking
from app.services.sla_service import sla_if_running


dca_bp = Blueprint("dca", __name__)

@dca_bp.route("/cases", methods=["GET"])
def get_assigned_cases():
    # 1. Role check
    if session.get("role") != "DCA":
        abort(403)

    # 2. Logged-in user
    user = User.query.get(session.get("user_id"))
    if not user or not user.organization_id:
        return jsonify([])

    # 3. Active assignments for this DCA organization
    assignments = (
        CaseAssignment.query
        .filter(
            CaseAssignment.dca_id == user.organization_id,
            CaseAssignment.unassigned_at.is_(None)
        )
        .all()
    )

    # 4. Build response
    result = []
    for a in assignments:
        case = DebtCase.query.get(a.case_id)
        if not case:
            continue

        result.append({
            "id": case.id,
            "case_id": case.tracking_number,
            "customer": case.customer_name,
            "amount": case.amount_due,
            "aging": case.aging_days,
            "priority": (
                case.prediction.priority_score
                if case.prediction else "Medium"
            ),
            "status": case.status
        })

    return jsonify(result)

@dca_bp.route("/cases/<int:case_id>", methods=["GET"])
def get_case(case_id):
    if session.get("role") != "DCA":
        abort(403)

    user = User.query.get(session.get("user_id"))
    if not user:
        abort(403)

    assignment = CaseAssignment.query.filter_by(
        case_id=case_id,
        dca_id=user.organization_id,
        unassigned_at=None
    ).first()

    if not assignment:
        abort(404)

    case = DebtCase.query.get(case_id)
    if not case:
        abort(404)

    return jsonify({
        "id": case.id,
        "case_id": case.tracking_number,
        "customer": case.customer_name,
        "status": case.status
    })

@dca_bp.route("/cases/<int:case_id>/update-status", methods=["POST"])
def update_case_status(case_id):
    if session.get("role") != "DCA":
        abort(403)

    data = request.get_json() or {}
    new_status = data.get("status")
    note = data.get("note")

    if not new_status:
        return jsonify({"error": "status is required"}), 400

    user = User.query.get(session.get("user_id"))
    assignment = CaseAssignment.query.filter_by(
        case_id=case_id,
        dca_id=user.organization_id,
        unassigned_at=None
    ).first()

    if not assignment:
        abort(403)

    case = DebtCase.query.get(case_id)
    if not case:
        abort(404)

    # ✅ Allowed transitions for DCA
    allowed = {"Pending", "Paid", "Escalate"}
    if new_status not in allowed:
        return jsonify({"error": "Invalid status"}), 400

    case.status = "ESCALATED" if new_status == "Escalate" else new_status

    # ✅ Audit log
    db.session.add(AuditLog(
        entity_type="DebtCase",
        entity_id=case.id,
        action="DCA_STATUS_UPDATE",
        performed_by=session["user_id"],
        performed_at=datetime.utcnow(),
        audit_metadata={
            "new_status": new_status,
            "note": note
        }
    ))

    db.session.commit()
    return jsonify({"status": "updated"})

@dca_bp.route("/cases/<int:case_id>/notes", methods=["POST"])
def add_note(case_id):
    if session.get("role") != "DCA":
        abort(403)

    data = request.get_json(silent=True) or {}
    note = data.get("note")

    if not note:
        return jsonify({"error": "note is required"}), 400

    user_id = session.get("user_id")

    # Activity log
    db.session.add(CaseActivityLog(
        case_id=case_id,
        performed_by=user_id,
        action_type="NOTE",
        description=note,
        created_at=datetime.utcnow()
    ))

    # ✅ Complete SLA
    sla_if_running(case_id)

    db.session.commit()
    return jsonify({"status": "note added"})


@dca_bp.route("/cases/<int:case_id>/request-escalation", methods=["POST"])
def request_case_escalation(case_id):
    if session.get("role") != "DCA":
        abort(403)

    data = request.get_json(silent=True) or {}
    reason = data.get("reason")

    if not reason:
        return jsonify({"error": "Escalation reason is required"}), 400

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if not user:
        abort(403)

    assignment = CaseAssignment.query.filter_by(
        case_id=case_id,
        dca_id=user.organization_id,
        unassigned_at=None
    ).first()

    if not assignment:
        abort(403)

    existing = CaseEscalation.query.filter_by(
        case_id=case_id,
        status="PENDING"
    ).first()

    if existing:
        return jsonify({"error": "Escalation already pending"}), 400

    # Persist escalation
    db.session.add(CaseEscalation(
        case_id=case_id,
        requested_by=user_id,
        reason=reason,
        status="PENDING",
        requested_at=datetime.utcnow()
    ))

    # ✅ Case activity log (IMPORTANT)
    db.session.add(CaseActivityLog(
        case_id=case_id,
        performed_by=user_id,
        action_type="STATUS_UPDATE",
        description=f"Escalation requested: {reason}",
        created_at=datetime.utcnow()
    ))

    # ✅ Complete SLA
    sla_if_running(case_id)

    # Audit log (enterprise visibility)
    db.session.add(AuditLog(
        entity_type="DebtCase",
        entity_id=str(case_id),
        action="DCA_ESCALATION_REQUESTED",
        performed_by=user_id,
        performed_at=datetime.utcnow(),
        audit_metadata={
            "reason": reason[:120]
        }
    ))

    db.session.commit()
    return jsonify({"status": "escalation_requested"})



