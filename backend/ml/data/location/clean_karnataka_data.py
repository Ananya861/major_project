import pandas as pd
import os

print("Loading processed Karnataka dataset...")

input_file = "ml/data/location/processed/karnataka_crop_production.csv"
output_file = "ml/data/location/processed/karnataka_crop_production_clean.csv"

df = pd.read_csv(input_file)

print("Original shape:", df.shape)

# Remove exact duplicate rows
df = df.drop_duplicates()

print("After removing exact duplicates:", df.shape)

# Columns that identify the same agricultural record
key_columns = [
    "State_Name",
    "District_Name",
    "Crop_Year",
    "Season",
    "Crop",
    "Area"
]

# Sort by production so the smaller/original-scale record is kept
df = df.sort_values(
    by="Production"
)

# Remove duplicate agricultural records
df = df.drop_duplicates(
    subset=key_columns,
    keep="first"
)

print("After removing duplicate crop records:", df.shape)

# Reset index
df = df.reset_index(drop=True)

# Create output directory if needed
os.makedirs(
    "ml/data/location/processed",
    exist_ok=True
)

# Save cleaned dataset
df.to_csv(
    output_file,
    index=False
)

print("\nCleaning completed successfully!")

print("\nFinal dataset shape:")
print(df.shape)

print("\nYears:")
print(sorted(df["Crop_Year"].unique()))

print("\nDistricts:")
print(df["District_Name"].nunique())

print("\nCrops:")
print(df["Crop"].nunique())

print("\nDuplicate agricultural records:")
print(
    df.duplicated(
        subset=key_columns
    ).sum()
)

print("\nSaved cleaned dataset to:")
print(os.path.abspath(output_file))