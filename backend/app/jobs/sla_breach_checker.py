from datetime import datetime, timedelta
from app import db
from app.models.sla import CaseSLATracking
from app.models.audit_log import AuditLog

def check_sla_breaches():
    now = datetime.utcnow()

    running_slas = CaseSLATracking.query.filter_by(status="RUNNING").all()

    for sla in running_slas:
        max_hours = sla.sla_definition.max_resolution_hours
        deadline = sla.started_at + timedelta(hours=max_hours)

        if now > deadline:
            sla.status = "BREACHED"
            sla.breached_at = now
            db.session.add(sla)

            # ✅ Audit log for FedEx compliance
            db.session.add(AuditLog(
                entity_type="SLA",
                entity_id=str(sla.case_id),
                action="SLA_BREACHED",
                performed_at=now,
                audit_metadata={
                    "sla_definition_id": sla.sla_definition_id,
                    "max_resolution_hours": max_hours
                }
            ))

    db.session.commit()

