import json
from pathlib import Path

import pandas as pd


# Project paths
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"

INPUT_FILES = [
    "soyabean_biaora.json",
    "wheat_khilchipur.json",
    "maize_jaspur.json",
    "groundnut_sendhwa.json",
]

OUTPUT_FILE = DATA_DIR / "mandi_prices.csv"


def load_json_file(file_path: Path) -> pd.DataFrame:
    """Load one Government Mandi JSON file into a DataFrame."""

    with open(file_path, "r", encoding="utf-8-sig") as file:
        records = json.load(file)

    df = pd.DataFrame(records)

    return df


def main():
    dataframes = []

    print("Loading official Mandi datasets...\n")

    for filename in INPUT_FILES:
        file_path = DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = load_json_file(file_path)

        print(f"{filename}: {len(df)} records")

        dataframes.append(df)

    # Combine all four datasets
    data = pd.concat(dataframes, ignore_index=True)

    print(f"\nCombined records: {len(data)}")

    # Keep only the columns required for forecasting
    required_columns = [
        "Arrival_Date",
        "Commodity",
        "Market",
        "Min_Price",
        "Max_Price",
        "Modal_Price",
        "State",
        "District",
    ]

    data = data[required_columns]

    # Convert date
    data["Arrival_Date"] = pd.to_datetime(
        data["Arrival_Date"],
        format="%d/%m/%Y",
        errors="coerce",
    )

    # Convert prices to numeric
    price_columns = [
        "Min_Price",
        "Max_Price",
        "Modal_Price",
    ]

    for column in price_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    # Remove invalid rows
    data = data.dropna(
        subset=[
            "Arrival_Date",
            "Commodity",
            "Market",
            "Modal_Price",
        ]
    )

    # Remove impossible/non-positive prices
    data = data[
        (data["Min_Price"] > 0)
        & (data["Max_Price"] > 0)
        & (data["Modal_Price"] > 0)
    ]

    # Remove duplicate records
    data = data.drop_duplicates()

    # Sort chronologically within each crop/market
    data = data.sort_values(
        by=["Commodity", "Market", "Arrival_Date"]
    ).reset_index(drop=True)

    # Save cleaned combined dataset
    data.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print("\nData preparation completed successfully!")
    print(f"Final records: {len(data)}")
    print(f"Output file: {OUTPUT_FILE}")

    print("\nRecords by crop:")
    print(data.groupby("Commodity").size())

    print("\nDate range:")
    print(data["Arrival_Date"].min().date(), "to", data["Arrival_Date"].max().date())


if __name__ == "__main__":
    main()