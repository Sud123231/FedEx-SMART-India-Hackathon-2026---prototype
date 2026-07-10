from . import db
from datetime import datetime
from .organization import Organization


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(150), unique=True, nullable=False)

    # THIS is what decides dashboard
    role = db.Column(
        db.Enum("ENTERPRISE", "DCA", name="user_role"),
        nullable=False
    )

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organizations.id",ondelete="CASCADE"),
        nullable=True
    )

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)