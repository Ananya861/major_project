"""
Train crop classifiers offline and save the best sklearn Pipeline.

Run from the backend directory (does not run when the API starts):

    python -m ml.train
"""

from __future__ import annotations

import json

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split

from ml.evaluate import compute_classification_metrics, save_metrics
from ml.preprocess import (
    ARTIFACT_DIR,
    NUMERIC_FEATURES,
    PIPELINE_PATH,
    RANDOM_STATE,
    build_model_pipeline,
    load_training_frame,
)


def _candidate_estimators() -> list[tuple[str, object]]:
    return [
        (
            "RandomForestClassifier",
            RandomForestClassifier(
                n_estimators=200,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
        (
            "GradientBoostingClassifier",
            GradientBoostingClassifier(random_state=RANDOM_STATE),
        ),
    ]


def main() -> None:
    X, y = load_training_frame()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    comparison: list[dict] = []
    fitted: list[tuple[str, object, dict]] = []

    for name, estimator in _candidate_estimators():
        pipeline = build_model_pipeline(estimator)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)
        class_names = [str(c) for c in pipeline.classes_]
        metrics = compute_classification_metrics(
            y_test,
            y_pred,
            labels=class_names,
            y_proba=y_proba,
            top_k=3,
        )
        summary = {
            "estimator": name,
            "accuracy": metrics["accuracy"],
            "f1_macro": metrics["f1_macro"],
            "precision_macro": metrics["precision_macro"],
            "recall_macro": metrics["recall_macro"],
            "top_3_accuracy": metrics.get("top_k_accuracy", {}).get("score"),
        }
        comparison.append(summary)
        fitted.append((name, pipeline, metrics))
        print(f"{name}: accuracy={summary['accuracy']:.4f} f1_macro={summary['f1_macro']:.4f}")

    best_name, best_pipeline, best_metrics = max(fitted, key=lambda item: item[2]["f1_macro"])
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {
        "pipeline": best_pipeline,
        "feature_names": NUMERIC_FEATURES,
        "estimator_name": best_name,
        "random_state": RANDOM_STATE,
        "target": "label",
        "notes": (
            "Trained on Kaggle crop recommendation CSV. "
            "API moisture is a humidity fallback only; soil_type is not in the dataset."
        ),
    }
    joblib.dump(bundle, PIPELINE_PATH)

    artifact_metrics = {
        "selected_estimator": best_name,
        "selection_criterion": "f1_macro",
        "random_state": RANDOM_STATE,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "n_classes": int(len(best_pipeline.classes_)),
        "classes": [str(c) for c in best_pipeline.classes_],
        "comparison": comparison,
        "test_metrics": best_metrics,
        "artifact": str(PIPELINE_PATH.as_posix()),
    }
    save_metrics(artifact_metrics)
    print(json.dumps({"selected": best_name, "artifact": str(PIPELINE_PATH)}, indent=2))


if __name__ == "__main__":
    main()
