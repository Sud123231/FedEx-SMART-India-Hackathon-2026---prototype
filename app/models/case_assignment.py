from . import db
from datetime import datetime

class CaseAssignment(db.Model):
    __tablename__ = "case_assignments"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("debt_cases.id"), nullable=False)
    dca_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    unassigned_at = db.Column(db.DateTime)
