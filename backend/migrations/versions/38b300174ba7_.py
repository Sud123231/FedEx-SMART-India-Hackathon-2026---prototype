"""
empty message

Revision ID: 38b300174ba7
Revises: 5193ee3e1140
Create Date: 2026-01-10 09:23:51.625964
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = '38b300174ba7'
down_revision = '5193ee3e1140'
branch_labels = None
depends_on = None

# ----------------------------
# EXISTING ENUM (DO NOT CREATE)
# ----------------------------
activity_type_enum = ENUM(
    'STATUS_UPDATE',
    'NOTE',
    'CALL',
    'EMAIL',
    'VISIT',
    name='activity_type',
    create_type=False   # 🔑 critical fix
)

def upgrade():
    op.create_table(
        'case_activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('performed_by', sa.Integer(), nullable=True),
        sa.Column('action_type', activity_type_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['case_id'],
            ['debt_cases.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['performed_by'],
            ['users.id']
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # ⚠️ COMMENTED FOR SAFETY — enable later if truly obsolete
    # op.drop_table('cases')
    # op.drop_table('notes')
    # op.drop_table('escalations')


def downgrade():
    op.drop_table('case_activity_logs')
