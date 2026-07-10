from app import db
from app.models.all_models import CaseSLATracking
from app.models.all_models import AuditLog
from datetime import datetime

def sla_if_running(case_id):
    sla = CaseSLATracking.query.filter_by(
        case_id=case_id,
        status="RUNNING"
    ).first()

    if sla:
        sla.status = "COMPLETED"
        db.session.add(sla)

        # ✅ Audit log
        db.session.add(AuditLog(
            entity_type="SLA",
            entity_id=str(case_id),
            action="SLA_COMPLETED",
            performed_at=datetime.utcnow(),
            audit_metadata={
                "sla_definition_id": sla.sla_definition_id
            }
        ))
