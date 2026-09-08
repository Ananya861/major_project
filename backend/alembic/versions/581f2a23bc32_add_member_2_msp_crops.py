"""add Member 2 MSP crops

Revision ID: 581f2a23bc32
Revises: f26cbc9d172e
"""

from alembic import op


revision = "581f2a23bc32"
down_revision = "f26cbc9d172e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO crop (name, season)
        VALUES
            ('Mustard', 'rabi'),
            ('Bengal Gram(Gram)(Whole)', 'rabi'),
            ('Green Gram(Moong)(Whole)', 'kharif'),
            ('Potato', 'year-round'),
            ('Garlic', 'year-round')
        ON CONFLICT (name) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM crop
        WHERE name IN (
            'Mustard',
            'Bengal Gram(Gram)(Whole)',
            'Green Gram(Moong)(Whole)',
            'Potato',
            'Garlic'
        )
        """
    )