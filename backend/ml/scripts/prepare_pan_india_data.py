import json
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

INPUT_DIR = Path("ml/data/pan_india")

OUTPUT_FILE = Path(
    "ml/data/pan_india_combined.csv"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

COLUMNS = [
    "Arrival_Date",
    "Commodity",
    "Market",
    "Min_Price",
    "Max_Price",
    "Modal_Price",
    "State",
    "District",
    "Variety",
    "Grade",
]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PAN-INDIA DATA CLEANING")
    print("=" * 70)

    files = [
        file
        for file in INPUT_DIR.glob("*.json")
        if file.name != "_progress.json"
    ]

    print(
        f"JSON files found: {len(files)}"
    )

    if not files:
        raise RuntimeError(
            "No JSON files found in "
            f"{INPUT_DIR}"
        )

    dataframes = []

    # --------------------------------------------------------
    # READ ALL JSON FILES
    # --------------------------------------------------------

    for index, file in enumerate(
        files,
        start=1,
    ):

        try:

            with file.open(
                "r",
                encoding="utf-8",
            ) as f:

                records = json.load(f)

            if not records:
                continue

            df = pd.DataFrame(records)

            # Add missing columns if necessary.
            for column in COLUMNS:

                if column not in df.columns:
                    df[column] = None

            df = df[COLUMNS]

            dataframes.append(df)

            if index % 100 == 0:
                print(
                    f"Processed "
                    f"{index}/{len(files)} files..."
                )

        except Exception as exc:

            print(
                f"Skipping {file.name}: "
                f"{exc}"
            )

    if not dataframes:

        raise RuntimeError(
            "No usable JSON data found."
        )

    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    print()
    print("Combining datasets...")

    df = pd.concat(
        dataframes,
        ignore_index=True,
    )

    print(
        f"Raw combined records: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # CLEAN TEXT COLUMNS
    # --------------------------------------------------------

    text_columns = [
        "Commodity",
        "Market",
        "State",
        "District",
        "Variety",
        "Grade",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # CLEAN DATE
    # --------------------------------------------------------

    df["Arrival_Date"] = pd.to_datetime(
        df["Arrival_Date"],
        dayfirst=True,
        errors="coerce",
    )

    # --------------------------------------------------------
    # CLEAN PRICE COLUMNS
    # --------------------------------------------------------

    price_columns = [
        "Min_Price",
        "Max_Price",
        "Modal_Price",
    ]

    for column in price_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # REMOVE INVALID RECORDS
    # --------------------------------------------------------

    before = len(df)

    df = df.dropna(
        subset=[
            "Arrival_Date",
            "Commodity",
            "Market",
            "State",
            "District",
            "Min_Price",
            "Max_Price",
            "Modal_Price",
        ]
    )

    print(
        f"Removed missing/invalid records: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # REMOVE INVALID PRICES
    # --------------------------------------------------------

    before = len(df)

    df = df[
        (df["Min_Price"] >= 0)
        & (df["Max_Price"] >= 0)
        & (df["Modal_Price"] >= 0)
    ]

    print(
        f"Removed negative-price records: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # REMOVE IMPOSSIBLE PRICE ORDERING
    # --------------------------------------------------------

    before = len(df)

    df = df[
        (df["Min_Price"] <= df["Max_Price"])
        & (df["Modal_Price"] >= df["Min_Price"])
        & (df["Modal_Price"] <= df["Max_Price"])
    ]

    print(
        f"Removed inconsistent price records: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # REMOVE EXACT DUPLICATES
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates()

    print(
        f"Removed exact duplicates: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "Commodity",
            "State",
            "District",
            "Market",
            "Arrival_Date",
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # FORMAT DATE
    # --------------------------------------------------------

    df["Arrival_Date"] = (
        df["Arrival_Date"]
        .dt.strftime("%Y-%m-%d")
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)

    print(
        f"Final records: {len(df)}"
    )

    print(
        f"Unique commodities: "
        f"{df['Commodity'].nunique()}"
    )

    print(
        f"Unique states: "
        f"{df['State'].nunique()}"
    )

    print(
        f"Unique markets: "
        f"{df['Market'].nunique()}"
    )

    print(
        f"Date range: "
        f"{df['Arrival_Date'].min()} "
        f"to "
        f"{df['Arrival_Date'].max()}"
    )

    print(
        f"Output file: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()