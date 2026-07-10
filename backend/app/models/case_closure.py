from . import db
from datetime import datetime

class CaseClosure(db.Model):
    __tablename__ = "case_closures"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("debt_cases.id",ondelete="CASCADE"), unique=True)
    recovered_amount = db.Column(db.Float)
    closure_reason = db.Column(db.String(255))
    closed_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    closed_at = db.Column(db.DateTime, default=datetime.utcnow)
