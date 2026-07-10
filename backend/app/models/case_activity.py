from . import db
from datetime import datetime

class CaseActivityLog(db.Model):
    __tablename__ = "case_activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("debt_cases.id", ondelete="CASCADE"),
        nullable=False
    )

    performed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    action_type = db.Column(
        db.Enum(
            "STATUS_UPDATE",
            "NOTE",
            "CALL",
            "EMAIL",
            "VISIT",
            name="activity_type"
        ),
        nullable=False
    )

    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    performer = db.relationship(
        "User",
        backref="performed_case_activities"
    )

