"""add mustard market reference

Revision ID: 28aebd0f364f
Revises: 581f2a23bc32
"""

from alembic import op


revision = "28aebd0f364f"
down_revision = "581f2a23bc32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO market (name, state, district)
        VALUES ('Asansol APMC', 'West Bengal', 'Paschim Bardhaman')
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM market
        WHERE name = 'Asansol APMC'
          AND state = 'West Bengal'
          AND district = 'Paschim Bardhaman'
        """
    )