"""Runtime crop-recommendation inference (loads a pre-trained joblib pipeline)."""

from app.ml.crop_inference import CropModelNotAvailable, recommend_crops

__all__ = ["CropModelNotAvailable", "recommend_crops"]
