"""add crop classes for model

Revision ID: f26cbc9d172e
Revises: 001_initial
Create Date: 2026-09-03 14:07:00.791129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f26cbc9d172e"
down_revision: Union[str, Sequence[str], None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MODEL_CROPS = [
    "Apple",
    "Banana",
    "Blackgram",
    "Chickpea",
    "Coconut",
    "Coffee",
    "Cotton",
    "Grapes",
    "Jute",
    "Kidneybeans",
    "Lentil",
    "Maize",
    "Mango",
    "Mothbeans",
    "Mungbean",
    "Muskmelon",
    "Orange",
    "Papaya",
    "Pigeonpeas",
    "Pomegranate",
    "Rice",
    "Watermelon",
]


def upgrade() -> None:
    crop_table = sa.table(
        "crop",
        sa.column("name", sa.String(length=100)),
        sa.column("season", sa.String(length=50)),
    )

    existing = {
        "Wheat",
        "Rice",
        "Tomato",
        "Onion",
        "Cotton",
    }

    rows = [
        {"name": crop, "season": None}
        for crop in MODEL_CROPS
        if crop not in existing
    ]

    if rows:
        op.bulk_insert(crop_table, rows)


def downgrade() -> None:
    crop_table = sa.table(
        "crop",
        sa.column("name", sa.String(length=100)),
    )

    op.execute(
        crop_table.delete().where(
            crop_table.c.name.in_(MODEL_CROPS)
        )
    )