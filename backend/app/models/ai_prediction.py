from . import db
from datetime import datetime

class AIModelPrediction(db.Model):
    __tablename__ = "ai_model_predictions"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(          
        db.Integer,
        db.ForeignKey("debt_cases.id",ondelete="CASCADE"),
        unique=True,
        nullable=False
    )


    model_version = db.Column(db.String(50), nullable=False)

    predicted_recovery_probability = db.Column(db.Float, nullable=False)
    priority_score = db.Column(db.Float, nullable=False)

    predicted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
