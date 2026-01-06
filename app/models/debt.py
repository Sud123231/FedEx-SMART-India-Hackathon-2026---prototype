from . import db
from datetime import datetime

class DebtCase(db.Model):
    __tablename__ = "debt_cases"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Case info
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="Pending")  # e.g., Pending, Collected, Disputed

    # Optional extended fields
    aging_days = db.Column(db.Integer)
    aging_bucket = db.Column(db.Enum("0-30","31-60","61-90","90+", name="aging_bucket"))
    priority_score = db.Column(db.Float)
    predicted_recovery_probability = db.Column(db.Float)

    # Assignment
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

    # Relationships
    assigned_agent = db.relationship("User", foreign_keys=[assigned_agent_id], backref="assigned_debt_cases")
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_debt_cases")

"""
class DebtCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100))
    amount_due = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="Pending") # e.g., Pending, Collected, Disputed
    
    # Link to the user who uploaded it or is assigned to it
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'))  """     