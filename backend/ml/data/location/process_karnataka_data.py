import pandas as pd
from pathlib import Path


# Paths
BASE_DIR = Path(__file__).resolve().parent

RAW_FILE = BASE_DIR / "raw" / "Indian_crop_production_yield_dataset.csv"

PROCESSED_FILE = (
    BASE_DIR / "processed" / "karnataka_crop_production.csv"
)


print("Loading dataset...")

df = pd.read_csv(RAW_FILE)

print(f"Original dataset shape: {df.shape}")


# Filter only Karnataka
df["State_Name"] = df["State_Name"].str.strip()

karnataka_df = df[
    df["State_Name"].str.lower() == "karnataka"
].copy()

print(f"Karnataka dataset shape: {karnataka_df.shape}")


# Clean text columns
text_columns = [
    "State_Name",
    "District_Name",
    "Season",
    "Crop"
]

for column in text_columns:
    karnataka_df[column] = (
        karnataka_df[column]
        .astype(str)
        .str.strip()
    )


# Standardize district names
district_mapping = {

    "BAGALKOTE": "BAGALKOT",
    "BELGAUM": "BELAGAVI",
    "BELLARY": "BALLARI",
    "BANGALORE RURAL": "BENGALURU RURAL",
    "BIJAPUR": "VIJAYAPURA",
    "CHAMARAJANAGARA": "CHAMARAJANAGAR",
    "CHIKKABALLAPURA": "CHIKBALLAPUR",
    "CHIKMAGALUR": "CHIKKAMAGALURU",
    "DAKSHIN KANNAD": "DAKSHINA KANNADA",
    "GULBARGA": "KALABURAGI",
    "MYSORE": "MYSURU",
    "SHIMOGA": "SHIVAMOGGA",
    "TUMKUR": "TUMAKURU",
    "UTTAR KANNAD": "UTTARA KANNADA",
    "YADGIR": "YADAGIRI"
}

karnataka_df["District_Name"] = (
    karnataka_df["District_Name"]
    .replace(district_mapping)
)


# Standardize a few crop names
crop_mapping = {

    "Paddy": "Rice",
    "Arhar/Tur": "Tur",
    "Moong(Green Gram)": "Moong",
    "Cotton(lint)": "Cotton",
    "Horse-gram": "Horse Gram",
    "Other  Rabi pulses": "Other Rabi Pulses",
    "Other Kharif pulses": "Other Kharif Pulses",
    "Other Rabi pulses": "Other Rabi Pulses"
}

karnataka_df["Crop"] = (
    karnataka_df["Crop"]
    .replace(crop_mapping)
)


# Sort data
karnataka_df = karnataka_df.sort_values(
    by=[
        "District_Name",
        "Crop_Year",
        "Season",
        "Crop"
    ]
)


# Reset index
karnataka_df = karnataka_df.reset_index(drop=True)


# Save processed dataset
PROCESSED_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

karnataka_df.to_csv(
    PROCESSED_FILE,
    index=False
)


# Summary
print("\nProcessing completed successfully.")

print("\nProcessed dataset shape:")
print(karnataka_df.shape)

print("\nYears:")
print(
    sorted(karnataka_df["Crop_Year"].unique())
)

print("\nNumber of districts:")
print(karnataka_df["District_Name"].nunique())

print("\nDistricts:")
print(
    sorted(karnataka_df["District_Name"].unique())
)

print("\nNumber of crops:")
print(karnataka_df["Crop"].nunique())

print("\nSeasons:")
print(
    sorted(karnataka_df["Season"].unique())
)

print("\nMissing values:")
print(karnataka_df.isnull().sum())

print(f"\nSaved processed file to:\n{PROCESSED_FILE}")