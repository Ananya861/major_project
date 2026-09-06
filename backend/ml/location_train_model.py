import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


print("=" * 60)
print("KARNATAKA CROP YIELD PREDICTION MODEL TRAINING")
print("=" * 60)


# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

DATA_FILE = "ml/data/location/processed/karnataka_crop_production_ml_ready.csv"

df = pd.read_csv(DATA_FILE)

print("\nDataset loaded successfully.")
print("Dataset shape:", df.shape)


# --------------------------------------------------
# 2. Select features and target
# --------------------------------------------------

features = [
    "District_Name",
    "Crop",
    "Season",
    "Crop_Year"
]

target = "yield"

X = df[features]
y = df[target]


# --------------------------------------------------
# 3. Log transform target
# --------------------------------------------------

y_log = np.log1p(y)

print("\nUsing log1p transformation on yield.")


# --------------------------------------------------
# 4. Train-test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_log,
    test_size=0.20,
    random_state=42
)

print("\nTraining samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])


# --------------------------------------------------
# 5. Define categorical and numerical features
# --------------------------------------------------

categorical_features = [
    "District_Name",
    "Crop",
    "Season"
]

numerical_features = [
    "Crop_Year"
]


# --------------------------------------------------
# 6. Preprocessing
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# --------------------------------------------------
# 7. Random Forest model
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)


# --------------------------------------------------
# 8. Create pipeline
# --------------------------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# --------------------------------------------------
# 9. Train model
# --------------------------------------------------

print("\nTraining Random Forest model...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed successfully.")


# --------------------------------------------------
# 10. Predictions
# --------------------------------------------------

y_pred_log = pipeline.predict(X_test)

# Convert predictions back to original yield scale

y_test_original = np.expm1(y_test)
y_pred_original = np.expm1(y_pred_log)


# --------------------------------------------------
# 11. Evaluation
# --------------------------------------------------

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
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")


# --------------------------------------------------
# 12. Save model
# --------------------------------------------------

MODEL_DIR = "ml/models"

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "karnataka_yield_model.pkl"
)

joblib.dump(
    pipeline,
    MODEL_FILE
)


print("\nModel saved successfully:")
print(os.path.abspath(MODEL_FILE))


# --------------------------------------------------
# 13. Test prediction
# --------------------------------------------------

sample = pd.DataFrame([
    {
        "District_Name": "BELAGAVI",
        "Crop": "Maize",
        "Season": "Kharif",
        "Crop_Year": 2020
    }
])

prediction_log = pipeline.predict(sample)

prediction = np.expm1(prediction_log[0])

print("\n" + "=" * 60)
print("SAMPLE PREDICTION")
print("=" * 60)

print(sample.to_string(index=False))

print(f"\nPredicted Yield: {prediction:.2f}")


print("\nModel training pipeline completed!")