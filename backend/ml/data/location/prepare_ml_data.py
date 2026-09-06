import pandas as pd
import os

print("Loading cleaned Karnataka dataset...")

INPUT_FILE = "ml/data/location/processed/karnataka_crop_production_clean.csv"
OUTPUT_FILE = "ml/data/location/processed/karnataka_crop_production_ml_ready.csv"

df = pd.read_csv(INPUT_FILE)

print("Initial shape:", df.shape)

# --------------------------------------------------
# 1. Remove records with invalid agricultural values
# --------------------------------------------------

df = df[
    (df["Area"] > 0) &
    (df["Production"] > 0) &
    (df["yield"] > 0)
].copy()

print("After removing zero/negative values:", df.shape)

# --------------------------------------------------
# 2. Remove unrealistic yield outliers
# --------------------------------------------------

Q1 = df["yield"].quantile(0.01)
Q99 = df["yield"].quantile(0.99)

print("\nYield lower bound (1%):", Q1)
print("Yield upper bound (99%):", Q99)

df = df[
    (df["yield"] >= Q1) &
    (df["yield"] <= Q99)
].copy()

print("After removing extreme yield outliers:", df.shape)

# --------------------------------------------------
# 3. Reset index
# --------------------------------------------------

df = df.reset_index(drop=True)

# --------------------------------------------------
# 4. Final validation
# --------------------------------------------------

print("\nFinal validation:")

print("Missing values:")
print(df.isnull().sum())

print("\nYears:")
print(sorted(df["Crop_Year"].unique()))

print("\nDistrict count:", df["District_Name"].nunique())
print("Crop count:", df["Crop"].nunique())
print("Season count:", df["Season"].nunique())

print("\nYield statistics:")
print(df["yield"].describe())

# --------------------------------------------------
# 5. Save ML-ready dataset
# --------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nML-ready dataset saved successfully:")
print(os.path.abspath(OUTPUT_FILE))

print("\nFinal shape:", df.shape)