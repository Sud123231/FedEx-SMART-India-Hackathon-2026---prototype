from . import db
from datetime import datetime

class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.Enum("ENTERPRISE", "DCA", name="org_type"), nullable=False)
    status = db.Column(db.Enum("ACTIVE", "SUSPENDED", name="org_status"), default="ACTIVE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship("User", backref="organization", lazy=True)
