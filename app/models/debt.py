from .user import db

class DebtCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100))
    amount_due = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="Pending") # e.g., Pending, Collected, Disputed
    
    # Link to the user who uploaded it or is assigned to it
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'))