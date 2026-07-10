from . import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50))  
    entity_id = db.Column(db.String(50))  #need to be fixed when entity will be deleted
    action = db.Column(db.String(100))
    performed_by = db.Column(db.Integer, db.ForeignKey("users.id"),nullable=True)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)
    audit_metadata = db.Column(db.JSON)
