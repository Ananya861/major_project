"""initial schema and seed crops/markets

Revision ID: 001_initial
Revises:
Create Date: 2026-09-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "farmer",
        sa.Column("farmer_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("village", sa.String(length=100), nullable=True),
        sa.Column("land_size_acres", sa.Float(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("preferred_language", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("farmer_id"),
    )
    op.create_index(op.f("ix_farmer_phone"), "farmer", ["phone"], unique=True)

    op.create_table(
        "crop",
        sa.Column("crop_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("season", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("crop_id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "market",
        sa.Column("market_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("market_id"),
    )

    op.create_table(
        "weather_log",
        sa.Column("weather_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("temp", sa.Float(), nullable=True),
        sa.Column("rainfall", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("forecast_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("weather_id"),
    )
    op.create_index(op.f("ix_weather_log_latitude"), "weather_log", ["latitude"], unique=False)
    op.create_index(op.f("ix_weather_log_longitude"), "weather_log", ["longitude"], unique=False)

    op.create_table(
        "farm",
        sa.Column("farm_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("area_acres", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmer.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("farm_id"),
    )
    op.create_index(op.f("ix_farm_farmer_id"), "farm", ["farmer_id"], unique=False)

    notification_type = postgresql.ENUM(
        "price_alert",
        "weather_alert",
        name="notification_type",
        create_type=False,
    )

    op.execute(
        "CREATE TYPE notification_type AS ENUM ('price_alert', 'weather_alert')"
    )

    op.create_table(
        "notification",
        sa.Column("notif_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmer.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("notif_id"),
    )
    op.create_index(op.f("ix_notification_farmer_id"), "notification", ["farmer_id"], unique=False)

    op.create_table(
        "soil_data",
        sa.Column("soil_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("ph", sa.Float(), nullable=True),
        sa.Column("nitrogen", sa.Float(), nullable=True),
        sa.Column("phosphorus", sa.Float(), nullable=True),
        sa.Column("potassium", sa.Float(), nullable=True),
        sa.Column("moisture", sa.Float(), nullable=True),
        sa.Column("soil_type", sa.String(length=80), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.farm_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("soil_id"),
    )
    op.create_index(op.f("ix_soil_data_farm_id"), "soil_data", ["farm_id"], unique=False)

    op.create_table(
        "market_price",
        sa.Column("price_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("crop_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("min_price", sa.Float(), nullable=True),
        sa.Column("max_price", sa.Float(), nullable=True),
        sa.Column("modal_price", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["crop_id"], ["crop.crop_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["market_id"], ["market.market_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("price_id"),
        sa.UniqueConstraint("crop_id", "market_id", "date", name="uq_market_price_crop_market_date"),
    )
    op.create_index(op.f("ix_market_price_crop_id"), "market_price", ["crop_id"], unique=False)
    op.create_index(op.f("ix_market_price_market_id"), "market_price", ["market_id"], unique=False)

    op.create_table(
        "price_prediction",
        sa.Column("prediction_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("crop_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("predicted_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("predicted_price", sa.Float(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["crop_id"], ["crop.crop_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["market_id"], ["market.market_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("prediction_id"),
    )
    op.create_index(op.f("ix_price_prediction_crop_id"), "price_prediction", ["crop_id"], unique=False)
    op.create_index(op.f("ix_price_prediction_market_id"), "price_prediction", ["market_id"], unique=False)

    op.create_table(
        "crop_recommendation",
        sa.Column("reco_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("crop_id", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.farm_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_id"], ["crop.crop_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("reco_id"),
    )
    op.create_index(op.f("ix_crop_recommendation_farm_id"), "crop_recommendation", ["farm_id"], unique=False)
    op.create_index(op.f("ix_crop_recommendation_crop_id"), "crop_recommendation", ["crop_id"], unique=False)

    crop_table = sa.table(
        "crop",
        sa.column("name", sa.String),
        sa.column("season", sa.String),
    )
    op.bulk_insert(
        crop_table,
        [
            {"name": "Wheat", "season": "rabi"},
            {"name": "Rice", "season": "kharif"},
            {"name": "Tomato", "season": "year-round"},
            {"name": "Onion", "season": "rabi"},
            {"name": "Cotton", "season": "kharif"},
        ],
    )

    market_table = sa.table(
        "market",
        sa.column("name", sa.String),
        sa.column("state", sa.String),
        sa.column("district", sa.String),
    )
    op.bulk_insert(
        market_table,
        [
            {"name": "Azadpur", "state": "Delhi", "district": "North Delhi"},
            {"name": "Pimpalgaon", "state": "Maharashtra", "district": "Nashik"},
            {"name": "Kolar", "state": "Karnataka", "district": "Kolar"},
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_crop_recommendation_crop_id"), table_name="crop_recommendation")
    op.drop_index(op.f("ix_crop_recommendation_farm_id"), table_name="crop_recommendation")
    op.drop_table("crop_recommendation")
    op.drop_index(op.f("ix_price_prediction_market_id"), table_name="price_prediction")
    op.drop_index(op.f("ix_price_prediction_crop_id"), table_name="price_prediction")
    op.drop_table("price_prediction")
    op.drop_index(op.f("ix_market_price_market_id"), table_name="market_price")
    op.drop_index(op.f("ix_market_price_crop_id"), table_name="market_price")
    op.drop_table("market_price")
    op.drop_index(op.f("ix_soil_data_farm_id"), table_name="soil_data")
    op.drop_table("soil_data")
    op.drop_index(op.f("ix_notification_farmer_id"), table_name="notification")
    op.drop_table("notification")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.drop_index(op.f("ix_farm_farmer_id"), table_name="farm")
    op.drop_table("farm")
    op.drop_index(op.f("ix_weather_log_longitude"), table_name="weather_log")
    op.drop_index(op.f("ix_weather_log_latitude"), table_name="weather_log")
    op.drop_table("weather_log")
    op.drop_table("market")
    op.drop_table("crop")
    op.drop_index(op.f("ix_farmer_phone"), table_name="farmer")
    op.drop_table("farmer")
