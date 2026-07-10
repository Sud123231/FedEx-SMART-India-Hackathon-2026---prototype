from . import db
from datetime import datetime

class DCAPerformanceMetric(db.Model):
    __tablename__ = "dca_performance_metrics"

    id = db.Column(db.Integer, primary_key=True)

    dca_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )

    recovery_rate = db.Column(db.Float)               # %
    avg_resolution_days = db.Column(db.Float)
    sla_breach_percentage = db.Column(db.Float)

    total_cases_assigned = db.Column(db.Integer)
    total_cases_closed = db.Column(db.Integer)

    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
