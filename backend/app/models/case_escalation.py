from . import db
from datetime import datetime

class CaseEscalation(db.Model):
    __tablename__ = "case_escalations"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("debt_cases.id",ondelete="CASCADE"), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    reason = db.Column(db.Text)

    status = db.Column(
        db.Enum("PENDING","APPROVED","REJECTED", name="escalation_status"),
        default="PENDING"
    )

    decision_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime)
