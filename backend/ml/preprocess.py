"""
Shared preprocessing for crop-recommendation training and the saved sklearn pipeline.

The fitted Pipeline (imputer + scaler + classifier) is what inference loads.
Do not reimplement scaling or imputation in the API layer.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.schema import FEATURE_BOUNDS, NUMERIC_FEATURES, TARGET_COLUMN

RANDOM_STATE = 42

BACKEND_ROOT = Path(__file__).resolve().parent.parent
RAW_DATASET_PATH = Path(__file__).resolve().parent / "data" / "raw" / "crop_recommendation.csv"
ARTIFACT_DIR = BACKEND_ROOT / "app" / "artifacts"
PIPELINE_PATH = ARTIFACT_DIR / "crop_pipeline.joblib"
METRICS_PATH = ARTIFACT_DIR / "crop_metrics.json"

REQUIRED_COLUMNS = NUMERIC_FEATURES + [TARGET_COLUMN]


def load_raw_dataset(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or RAW_DATASET_PATH
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Crop dataset not found at {csv_path}. See ml/data/raw/SOURCE.md."
        )
    df = pd.read_csv(csv_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()


def drop_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing target/features or numeric values outside agronomic bounds."""
    cleaned = df.dropna(subset=REQUIRED_COLUMNS).copy()
    for column, (low, high) in FEATURE_BOUNDS.items():
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned = cleaned[
            cleaned[column].notna()
            & (cleaned[column] >= low)
            & (cleaned[column] <= high)
        ]
    cleaned[TARGET_COLUMN] = cleaned[TARGET_COLUMN].astype(str).str.strip()
    cleaned = cleaned[cleaned[TARGET_COLUMN] != ""]
    return cleaned.reset_index(drop=True)


def load_training_frame(path: Path | None = None) -> tuple[pd.DataFrame, pd.Series]:
    df = drop_invalid_rows(load_raw_dataset(path))
    if df.empty:
        raise ValueError("No valid training rows remained after validation.")
    X = df[NUMERIC_FEATURES]
    y = df[TARGET_COLUMN]
    return X, y


def build_preprocessor() -> ColumnTransformer:
    """Numeric-only transformer. There are no categorical columns in this dataset."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    return ColumnTransformer(
        transformers=[("numeric", numeric_pipeline, NUMERIC_FEATURES)],
        remainder="drop",
    )


def build_model_pipeline(estimator) -> Pipeline:
    """Full train/serve pipeline: preprocess then classify."""
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("clf", estimator),
        ]
    )
