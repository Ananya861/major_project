from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# Paths
# --------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent

DATA_FILE = ML_DIR / "data" / "mandi_prices.csv"
MODEL_DIR = ML_DIR / "models"

MODEL_FILE = MODEL_DIR / "price_model.joblib"
METRICS_FILE = MODEL_DIR / "price_model_metrics.json"


# --------------------------------------------------
# Feature names
# --------------------------------------------------

FEATURE_COLUMNS = [
    "lag_1",
    "lag_2",
    "lag_3",
    "rolling_mean_3",
    "month",
    "day",
    "day_of_week",
]


def create_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-series features separately for each
    Commodity + Market price series.
    """

    data = data.copy()

    data["Arrival_Date"] = pd.to_datetime(data["Arrival_Date"])

    data = data.sort_values(
        ["Commodity", "Market", "Arrival_Date"]
    ).reset_index(drop=True)

    groups = data.groupby(
        ["Commodity", "Market"],
        group_keys=False
    )

    # Previous modal prices
    data["lag_1"] = groups["Modal_Price"].shift(1)
    data["lag_2"] = groups["Modal_Price"].shift(2)
    data["lag_3"] = groups["Modal_Price"].shift(3)

    # Mean of the previous 3 known prices.
    # shift(1) prevents the current target price from
    # leaking into the input features.
    data["rolling_mean_3"] = groups["Modal_Price"].transform(
        lambda series: series.shift(1).rolling(window=3).mean()
    )

    # Calendar features
    data["month"] = data["Arrival_Date"].dt.month
    data["day"] = data["Arrival_Date"].dt.day
    data["day_of_week"] = data["Arrival_Date"].dt.dayofweek

    # Rows at the beginning of each series do not yet
    # have three previous observations.
    data = data.dropna(
        subset=FEATURE_COLUMNS + ["Modal_Price"]
    ).reset_index(drop=True)

    return data


def main():

    print("Loading cleaned Mandi dataset...")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    print(f"Original records: {len(data)}")

    # Ensure numeric target
    data["Modal_Price"] = pd.to_numeric(
        data["Modal_Price"],
        errors="coerce"
    )

    data = data.dropna(subset=["Modal_Price"])

    print("\nCreating forecasting features...")

    data = create_features(data)

    print(f"Records after feature engineering: {len(data)}")

    # --------------------------------------------------
    # Chronological train/test split
    # --------------------------------------------------

    data = data.sort_values("Arrival_Date").reset_index(drop=True)

    split_index = int(len(data) * 0.80)

    train_data = data.iloc[:split_index].copy()
    test_data = data.iloc[split_index:].copy()

    X_train = train_data[FEATURE_COLUMNS]
    y_train = train_data["Modal_Price"]

    X_test = test_data[FEATURE_COLUMNS]
    y_test = test_data["Modal_Price"]

    print(f"\nTraining records: {len(train_data)}")
    print(f"Testing records : {len(test_data)}")

    print(
        "Training date range:",
        train_data["Arrival_Date"].min().date(),
        "to",
        train_data["Arrival_Date"].max().date()
    )

    print(
        "Testing date range :",
        test_data["Arrival_Date"].min().date(),
        "to",
        test_data["Arrival_Date"].max().date()
    )

    # --------------------------------------------------
    # Train model
    # --------------------------------------------------

    print("\nTraining Gradient Boosting model...")

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )

    model.fit(X_train, y_train)

    # --------------------------------------------------
    # Evaluate model
    # --------------------------------------------------

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    rmse = np.sqrt(
        mean_squared_error(y_test, predictions)
    )

    r2 = r2_score(y_test, predictions)

    print("\nMODEL EVALUATION")
    print("----------------")
    print(f"MAE  : {mae:.2f}")
    print(f"RMSE : {rmse:.2f}")
    print(f"R2   : {r2:.4f}")

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_package = {
        "model": model,
        "features": FEATURE_COLUMNS,
        "model_type": "GradientBoostingRegressor",
        "target": "Modal_Price",
    }

    joblib.dump(
        model_package,
        MODEL_FILE
    )

    # --------------------------------------------------
    # Save metrics
    # --------------------------------------------------

    metrics = {
        "model": "GradientBoostingRegressor",
        "total_records": int(len(data)),
        "training_records": int(len(train_data)),
        "testing_records": int(len(test_data)),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "features": FEATURE_COLUMNS,
        "training_start_date": str(
            train_data["Arrival_Date"].min().date()
        ),
        "training_end_date": str(
            train_data["Arrival_Date"].max().date()
        ),
        "testing_start_date": str(
            test_data["Arrival_Date"].min().date()
        ),
        "testing_end_date": str(
            test_data["Arrival_Date"].max().date()
        ),
    }

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(metrics, file, indent=4)

    print("\nModel training completed successfully!")

    print(f"\nSaved model:")
    print(MODEL_FILE)

    print("\nSaved evaluation metrics:")
    print(METRICS_FILE)


if __name__ == "__main__":
    main()