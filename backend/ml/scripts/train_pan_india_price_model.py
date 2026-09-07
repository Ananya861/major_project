from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path("ml/data/pan_india_combined.csv")
MODEL_DIR = Path("ml/models")
MODEL_PATH = MODEL_DIR / "price_model.joblib"
METRICS_PATH = MODEL_DIR / "price_model_metrics.json"

NUMERIC_FEATURES = [
    "lag_1",
    "lag_2",
    "lag_3",
    "rolling_mean_3",
    "month",
    "day",
    "day_of_week",
]

CATEGORICAL_FEATURES = [
    "Commodity",
    "State",
    "District",
    "Market",
]


def main():
    print("=" * 60)
    print("PAN-INDIA PRICE MODEL TRAINING")
    print("=" * 60)

    print("\nLoading data...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded records: {len(df)}")

    required_columns = [
        "Commodity",
        "State",
        "District",
        "Market",
        "Arrival_Date",
        "Modal_Price",
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["Arrival_Date"] = pd.to_datetime(
        df["Arrival_Date"],
        errors="coerce",
    )

    df["Modal_Price"] = pd.to_numeric(
        df["Modal_Price"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "Commodity",
            "State",
            "District",
            "Market",
            "Arrival_Date",
            "Modal_Price",
        ]
    )

    group_columns = [
        "Commodity",
        "State",
        "District",
        "Market",
    ]

    df = df.sort_values(
        group_columns + ["Arrival_Date"]
    ).reset_index(drop=True)

    print("\nCreating time-series features...")

    # Create lag features.
    for lag in [1, 2, 3]:
        df[f"lag_{lag}"] = (
            df.groupby(group_columns)["Modal_Price"]
            .shift(lag)
        )

    # Create rolling mean without target leakage.
    df["rolling_mean_3"] = (
        df.groupby(group_columns)["Modal_Price"]
        .transform(
            lambda x: x.shift(1).rolling(
                window=3,
                min_periods=3,
            ).mean()
        )
    )

    # Calendar features.
    df["month"] = df["Arrival_Date"].dt.month
    df["day"] = df["Arrival_Date"].dt.day
    df["day_of_week"] = df["Arrival_Date"].dt.dayofweek

    df = df.dropna(
        subset=[
            "lag_1",
            "lag_2",
            "lag_3",
            "rolling_mean_3",
        ]
    ).reset_index(drop=True)

    print(f"Feature rows: {len(df)}")

    # Chronological split.
    df = df.sort_values("Arrival_Date").reset_index(drop=True)

    split_index = int(len(df) * 0.80)

    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    print(f"Training rows: {len(train_df)}")
    print(f"Testing rows: {len(test_df)}")

    print(
        f"Training dates: "
        f"{train_df['Arrival_Date'].min().date()} "
        f"to "
        f"{train_df['Arrival_Date'].max().date()}"
    )

    print(
        f"Testing dates: "
        f"{test_df['Arrival_Date'].min().date()} "
        f"to "
        f"{test_df['Arrival_Date'].max().date()}"
    )

    X_train = train_df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ]
    y_train = train_df["Modal_Price"]

    X_test = test_df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ]
    y_test = test_df["Modal_Price"]

    print("\nPreparing categorical features...")

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),
        ]
    )

    print("Encoding training data...")

    X_train_encoded = preprocessor.fit_transform(X_train)

    print(
        f"Encoded feature count: "
        f"{X_train_encoded.shape[1]}"
    )

    print("\nTraining fast HistGradientBoosting model...")

    model = HistGradientBoostingRegressor(
        max_iter=250,
        learning_rate=0.08,
        max_leaf_nodes=31,
        l2_regularization=1.0,
        random_state=42,
    )

    model.fit(
        X_train_encoded,
        y_train,
    )

    print("Model training completed.")

    print("\nEvaluating model...")

    X_test_encoded = preprocessor.transform(X_test)

    predictions = model.predict(X_test_encoded)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions,
    )

    print("\nMODEL RESULTS")
    print("-" * 40)
    print(f"MAE : {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²  : {r2:.4f}")

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_bundle = {
        "model": model,
        "preprocessor": preprocessor,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "model_type": "HistGradientBoostingRegressor",
        "target": "Modal_Price",
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
    )

    metrics = {
        "model_type": "HistGradientBoostingRegressor",
        "records": int(len(df)),
        "training_rows": int(len(train_df)),
        "testing_rows": int(len(test_df)),
        "training_start": str(
            train_df["Arrival_Date"].min().date()
        ),
        "training_end": str(
            train_df["Arrival_Date"].max().date()
        ),
        "testing_start": str(
            test_df["Arrival_Date"].min().date()
        ),
        "testing_end": str(
            test_df["Arrival_Date"].max().date()
        ),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metrics,
            f,
            indent=2,
        )

    print("\nSaved model:")
    print(MODEL_PATH)

    print("\nSaved metrics:")
    print(METRICS_PATH)

    print("\n" + "=" * 60)
    print("PAN-INDIA PRICE MODEL TRAINING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()