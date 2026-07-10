from . import db

class SLADefinition(db.Model):
    __tablename__ = "sla_definitions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    max_resolution_hours = db.Column(db.Integer)
    escalation_threshold_hours = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    # SLA instances using this definition
    case_sla_trackings = db.relationship(
        "CaseSLATracking",
        backref="sla_definition"
    )


class CaseSLATracking(db.Model):
    __tablename__ = "case_sla_tracking"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("debt_cases.id",ondelete="CASCADE"))
    sla_definition_id = db.Column(db.Integer, db.ForeignKey("sla_definitions.id"))
    started_at = db.Column(db.DateTime)
    breached_at = db.Column(db.DateTime)
    status = db.Column(db.Enum("RUNNING","BREACHED","COMPLETED", name="sla_status"))
