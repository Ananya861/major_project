"""Load the saved crop pipeline and return top-k classes from predict_proba."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.ml.feature_builder import payload_to_frame

ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "crop_pipeline.joblib"


class CropModelNotAvailable(RuntimeError):
    """Raised when the trained joblib artifact is missing or unreadable."""


@lru_cache(maxsize=1)
def load_bundle() -> dict[str, Any]:
    if not ARTIFACT_PATH.is_file():
        raise CropModelNotAvailable(
            f"Crop model artifact not found at {ARTIFACT_PATH}. "
            "Train it with: python -m ml.train (from the backend directory)."
        )
    try:
        bundle = joblib.load(ARTIFACT_PATH)
    except Exception as exc:
        raise CropModelNotAvailable(f"Could not load crop model artifact: {exc}") from exc
    if "pipeline" not in bundle:
        raise CropModelNotAvailable("Crop model artifact is missing the 'pipeline' key.")
    return bundle


def recommend_crops(soil_data: dict, top_k: int = 3) -> list[dict]:
    """
    Return up to `top_k` crops as [{"crop": str, "confidence": float}, ...]
    sorted by probability descending. Does not train.
    """
    if not isinstance(soil_data, dict):
        raise ValueError("soil_data must be a dict of feature values")

    bundle = load_bundle()
    pipeline = bundle["pipeline"]
    frame: pd.DataFrame = payload_to_frame(soil_data)
    try:
        proba = pipeline.predict_proba(frame)[0]
    except Exception as exc:
        raise ValueError(f"Crop model inference failed: {exc}") from exc

    classes = [str(c) for c in pipeline.classes_]
    k = max(1, min(top_k, len(classes)))
    ranked_idx = sorted(range(len(classes)), key=lambda i: float(proba[i]), reverse=True)[:k]
    return [
        {
            "crop": _display_name(classes[i]),
            "confidence": round(float(proba[i]), 6),
        }
        for i in ranked_idx
    ]


def _display_name(label: str) -> str:
    """Keep seed-table matching case-insensitive; present a stable display name."""
    return label.replace("_", " ").strip().title()
