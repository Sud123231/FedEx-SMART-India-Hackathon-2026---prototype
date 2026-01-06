from . import db
from datetime import datetime

class AIModelPrediction(db.Model):
    __tablename__ = "ai_model_predictions"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("debt_cases.id"))
    model_version = db.Column(db.String(50))
    priority_score = db.Column(db.Float)
    recovery_probability = db.Column(db.Float)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
