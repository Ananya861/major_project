"""Evaluation helpers for crop classification (used by train.py and as a CLI)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.preprocess import METRICS_PATH, PIPELINE_PATH, load_training_frame


def compute_classification_metrics(
    y_true,
    y_pred,
    *,
    labels: list[str] | None = None,
    y_proba: np.ndarray | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    label_list = labels if labels is not None else sorted(set(y_true) | set(y_pred))
    report = classification_report(
        y_true,
        y_pred,
        labels=label_list,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=label_list)
    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "classification_report": report,
        "confusion_matrix": {
            "labels": list(label_list),
            "matrix": matrix.tolist(),
        },
    }
    if y_proba is not None and labels is not None:
        metrics["top_k_accuracy"] = {
            "k": top_k,
            "score": float(_top_k_accuracy(y_true, y_proba, labels, top_k)),
        }
    return metrics


def _top_k_accuracy(y_true, y_proba: np.ndarray, class_names: list[str], k: int) -> float:
    k = min(k, y_proba.shape[1])
    top_indices = np.argsort(y_proba, axis=1)[:, -k:]
    correct = 0
    name_to_index = {name: i for i, name in enumerate(class_names)}
    for row, true_label in zip(top_indices, y_true):
        true_idx = name_to_index.get(str(true_label))
        if true_idx is not None and true_idx in row:
            correct += 1
    return correct / len(y_true) if len(y_true) else 0.0


def save_metrics(metrics: dict[str, Any], path: Path | None = None) -> Path:
    out_path = path or METRICS_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return out_path


def evaluate_saved_pipeline() -> dict[str, Any]:
    """Re-score the saved artifact on a fresh stratified holdout (same random_state as train)."""
    from sklearn.model_selection import train_test_split

    from ml.preprocess import RANDOM_STATE

    if not PIPELINE_PATH.is_file():
        raise FileNotFoundError(f"No saved pipeline at {PIPELINE_PATH}. Run: python -m ml.train")

    bundle = joblib.load(PIPELINE_PATH)
    pipeline = bundle["pipeline"]
    X, y = load_training_frame()
    _X_train, X_test, _y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)
    class_names = [str(c) for c in pipeline.classes_]
    return compute_classification_metrics(
        y_test,
        y_pred,
        labels=class_names,
        y_proba=y_proba,
        top_k=3,
    )


if __name__ == "__main__":
    result = evaluate_saved_pipeline()
    save_metrics(result)
    print(json.dumps({k: result[k] for k in ("accuracy", "f1_macro", "precision_macro", "recall_macro")}, indent=2))
    print(f"Wrote {METRICS_PATH}")
