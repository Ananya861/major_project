import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


DATA_FILE = "ml/data/location/processed/karnataka_crop_production_ml_ready.csv"

df = pd.read_csv(DATA_FILE)

print("=" * 60)
print("TIME-BASED MODEL VALIDATION")
print("=" * 60)

# Features and target
features = [
    "District_Name",
    "Crop",
    "Season",
    "Crop_Year"
]

X = df[features]
y = np.log1p(df["yield"])

# Time-based split
train_df = df[df["Crop_Year"] <= 2016].copy()
test_df = df[df["Crop_Year"] >= 2017].copy()

X_train = train_df[features]
X_test = test_df[features]

y_train = np.log1p(train_df["yield"])
y_test = np.log1p(test_df["yield"])

print("\nTraining years:", sorted(train_df["Crop_Year"].unique()))
print("Testing years:", sorted(test_df["Crop_Year"].unique()))

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# Preprocessing
categorical_features = [
    "District_Name",
    "Crop",
    "Season"
]

numerical_features = [
    "Crop_Year"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# Model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)


pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


print("\nTraining model using historical years...")

pipeline.fit(X_train, y_train)


# Prediction
y_pred_log = pipeline.predict(X_test)

y_test_original = np.expm1(y_test)
y_pred_original = np.expm1(y_pred_log)


# Metrics
mae = mean_absolute_error(
    y_test_original,
    y_pred_original
)

rmse = np.sqrt(
    mean_squared_error(
        y_test_original,
        y_pred_original
    )
)

r2 = r2_score(
    y_test_original,
    y_pred_original
)


print("\n" + "=" * 60)
print("TIME-BASED MODEL PERFORMANCE")
print("=" * 60)

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")

print("\nValidation completed.")