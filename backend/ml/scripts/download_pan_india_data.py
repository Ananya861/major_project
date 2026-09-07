import json
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import urlencode


# ============================================================
# DATA.GOV.IN API ENDPOINTS
# ============================================================

HISTORICAL_URL = (
    "https://api.data.gov.in/resource/"
    "35985678-0d79-46b4-9ed6-6f13308a1d24"
)

CURRENT_URL = (
    "https://api.data.gov.in/resource/"
    "9ef84268-d588-465a-a308-a864a43d0070"
)


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_DIR = Path("ml/data/pan_india")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROGRESS_FILE = OUTPUT_DIR / "_progress.json"


# ============================================================
# API KEY
# ============================================================

API_KEY = os.environ.get("DATA_GOV_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "DATA_GOV_API_KEY is not configured."
    )


# ============================================================
# CROPS
# ============================================================

CROPS = [
    "Wheat",
    "Maize",
    "Soyabean",
    "Groundnut",
    "Rice",
    "Paddy(Common)",
    "Potato",
    "Onion",
    "Tomato",
    "Mustard",
    "Garlic",
    "Bengal Gram(Gram)(Whole)",
    "Green Gram(Moong)(Whole)",
]


# ============================================================
# SETTINGS
# ============================================================

PAGE_SIZE = 100

# Normal delay between successful API requests.
REQUEST_DELAY = 2.0

# Maximum number of retries.
MAX_RETRIES = 5

# curl timeout for one request.
CURL_TIMEOUT = 120

# Wait time after a rate-limit response.
RATE_LIMIT_WAIT = 30


# ============================================================
# PROGRESS
# ============================================================

def load_progress():

    if not PROGRESS_FILE.exists():
        return set()

    try:

        with PROGRESS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return set(
            data.get("completed", [])
        )

    except Exception:

        return set()


def save_progress(completed):

    with PROGRESS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "completed": sorted(
                    completed
                )
            },
            file,
            indent=2,
        )


# ============================================================
# API HELPER
# ============================================================

def get_records(client, url, params):

    last_error = None

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            full_url = (
                f"{url}?{urlencode(params)}"
            )

            completed = subprocess.run(
                [
                    "curl.exe",
                    "-s",
                    "--max-time",
                    str(CURL_TIMEOUT),
                    full_url,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            if completed.returncode != 0:

                raise RuntimeError(
                    "curl failed with code "
                    f"{completed.returncode}"
                )

            if not completed.stdout.strip():

                raise RuntimeError(
                    "Empty response from "
                    "data.gov.in"
                )

            data = json.loads(
                completed.stdout
            )

            # ------------------------------------------------
            # RATE LIMIT HANDLING
            # ------------------------------------------------

            error_message = str(
                data.get("error", "")
            ).lower()

            if (
                "rate limit" in error_message
                or "rate_limit" in error_message
            ):

                last_error = RuntimeError(
                    str(data)
                )

                print(
                    f"    Rate limit reached. "
                    f"Waiting {RATE_LIMIT_WAIT} "
                    f"seconds before retry "
                    f"{attempt}/{MAX_RETRIES}..."
                )

                time.sleep(
                    RATE_LIMIT_WAIT
                )

                continue

            # ------------------------------------------------
            # API STATUS
            # ------------------------------------------------

            if data.get("status") != "ok":

                raise RuntimeError(
                    str(data)
                )

            records = (
                data.get("records")
                or []
            )

            total = int(
                data.get("total")
                or 0
            )

            # Small delay after successful request.
            time.sleep(
                REQUEST_DELAY
            )

            return records, total

        except Exception as exc:

            last_error = exc

            print(
                f"    API attempt "
                f"{attempt}/{MAX_RETRIES} "
                f"failed: {exc}"
            )

            if attempt < MAX_RETRIES:

                wait_time = (
                    5 * attempt
                )

                print(
                    f"    Waiting "
                    f"{wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

    raise RuntimeError(
        "API request failed after "
        f"{MAX_RETRIES} attempts: "
        f"{last_error}"
    )


# ============================================================
# DISCOVER ALL CURRENT MARKETS
# ============================================================

def discover_current_markets(
    client,
    crop,
):

    print(
        f"Discovering markets for {crop}..."
    )

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": PAGE_SIZE,
        "filters[commodity]": crop,
    }

    records, total = get_records(
        client,
        CURRENT_URL,
        params,
    )

    all_records = list(records)

    offset = len(records)

    print(
        f"    First page: "
        f"{len(records)} records"
    )

    while offset < total:

        params["offset"] = offset

        records, _ = get_records(
            client,
            CURRENT_URL,
            params,
        )

        if not records:
            break

        all_records.extend(records)

        offset += len(records)

        print(
            f"    Discovered "
            f"{offset}/{total} records",
            end="\r",
        )

    print()

    markets = {}

    for record in all_records:

        state = (
            record.get("state")
            or ""
        ).strip()

        district = (
            record.get("district")
            or ""
        ).strip()

        market = (
            record.get("market")
            or ""
        ).strip()

        if (
            not state
            or not district
            or not market
        ):
            continue

        key = (
            state,
            district,
            market,
        )

        markets[key] = {
            "state": state,
            "district": district,
            "market": market,
        }

    return list(
        markets.values()
    )


# ============================================================
# DOWNLOAD HISTORICAL DATA
# ============================================================

def download_historical_market(
    client,
    crop,
    state,
    district,
    market,
):

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": PAGE_SIZE,
        "filters[State]": state,
        "filters[District]": district,
        "filters[Commodity]": crop,
        "filters[Market]": market,
        "sort[Arrival_Date]": "desc",
    }

    records, total = get_records(
        client,
        HISTORICAL_URL,
        params,
    )

    all_records = list(records)

    offset = len(records)

    while offset < total:

        params["offset"] = offset

        records, _ = get_records(
            client,
            HISTORICAL_URL,
            params,
        )

        if not records:
            break

        all_records.extend(records)

        offset += len(records)

    return all_records


# ============================================================
# CLEAN RECORD
# ============================================================

def clean_record(record):

    return {
        "Arrival_Date": record.get(
            "Arrival_Date"
        ),
        "Commodity": record.get(
            "Commodity"
        ),
        "Market": record.get(
            "Market"
        ),
        "Min_Price": record.get(
            "Min_Price"
        ),
        "Max_Price": record.get(
            "Max_Price"
        ),
        "Modal_Price": record.get(
            "Modal_Price"
        ),
        "State": record.get(
            "State"
        ),
        "District": record.get(
            "District"
        ),
        "Variety": record.get(
            "Variety"
        ),
        "Grade": record.get(
            "Grade"
        ),
    }


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def deduplicate_by_date(records):

    result = {}

    for record in records:

        date_value = record.get(
            "Arrival_Date"
        )

        if not date_value:
            continue

        if date_value not in result:

            result[date_value] = record

    return list(
        result.values()
    )


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(text):

    chars = []

    for char in text:

        if char.isalnum():

            chars.append(
                char.lower()
            )

        else:

            chars.append("_")

    return "".join(
        chars
    ).strip("_")


# ============================================================
# MAIN
# ============================================================

def main():

    completed = load_progress()

    total_files = 0
    total_records = 0
    total_markets = 0

    client = None

    print()
    print("=" * 70)
    print(
        "PAN-INDIA MANDI DATA DOWNLOADER"
    )
    print("=" * 70)

    print(
        f"Crops configured: "
        f"{len(CROPS)}"
    )

    print(
        f"Already completed: "
        f"{len(completed)}"
    )

    print(
        f"Output directory: "
        f"{OUTPUT_DIR}"
    )

    print(
        f"Request delay: "
        f"{REQUEST_DELAY} seconds"
    )

    print(
        f"Rate-limit wait: "
        f"{RATE_LIMIT_WAIT} seconds"
    )

    print("=" * 70)

    for crop in CROPS:

        print()
        print("=" * 70)
        print(
            f"CROP: {crop}"
        )
        print("=" * 70)

        try:

            markets = (
                discover_current_markets(
                    client,
                    crop,
                )
            )

        except Exception as exc:

            print(
                f"Discovery failed for "
                f"{crop}: {exc}"
            )

            continue

        print(
            f"Unique markets found: "
            f"{len(markets)}"
        )

        total_markets += len(
            markets
        )

        for index, market_info in enumerate(
            markets,
            start=1,
        ):

            state = market_info[
                "state"
            ]

            district = market_info[
                "district"
            ]

            market = market_info[
                "market"
            ]

            key = "|".join(
                [
                    crop,
                    state,
                    district,
                    market,
                ]
            )

            filename = (
                f"{safe_filename(state)}_"
                f"{safe_filename(district)}_"
                f"{safe_filename(market)}_"
                f"{safe_filename(crop)}.json"
            )

            output_path = (
                OUTPUT_DIR / filename
            )

            print()
            print(
                f"[{index}/{len(markets)}] "
                f"{state} | "
                f"{district} | "
                f"{market}"
            )

            # ------------------------------------------------
            # SKIP COMPLETED MARKET
            # ------------------------------------------------

            if (
                key in completed
                and output_path.exists()
            ):

                print(
                    "    Already downloaded - "
                    "skipping."
                )

                continue

            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            try:

                records = (
                    download_historical_market(
                        client,
                        crop,
                        state,
                        district,
                        market,
                    )
                )

            except Exception as exc:

                print(
                    f"    FAILED: {exc}"
                )

                continue

            # ------------------------------------------------
            # CLEAN
            # ------------------------------------------------

            cleaned = [
                clean_record(record)
                for record in records
            ]

            # ------------------------------------------------
            # VALID RECORDS ONLY
            # ------------------------------------------------

            cleaned = [
                record
                for record in cleaned
                if (
                    record["Arrival_Date"]
                    and record["Min_Price"]
                    not in (None, "")
                    and record["Max_Price"]
                    not in (None, "")
                    and record["Modal_Price"]
                    not in (None, "")
                )
            ]

            # ------------------------------------------------
            # ONE RECORD PER DATE
            # ------------------------------------------------

            cleaned = (
                deduplicate_by_date(
                    cleaned
                )
            )

            if not cleaned:

                print(
                    "    No usable historical "
                    "records."
                )

                # Mark this market as completed
                # so it is not repeatedly retried.
                completed.add(key)

                save_progress(
                    completed
                )

                continue

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            with output_path.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    cleaned,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            print(
                f"    Saved "
                f"{len(cleaned)} records."
            )

            # ------------------------------------------------
            # SAVE PROGRESS IMMEDIATELY
            # ------------------------------------------------

            completed.add(key)

            save_progress(
                completed
            )

            total_files += 1
            total_records += len(
                cleaned
            )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print(
        "PAN-INDIA DOWNLOAD COMPLETE"
    )
    print("=" * 70)

    print(
        f"Markets discovered: "
        f"{total_markets}"
    )

    print(
        f"Files downloaded this run: "
        f"{total_files}"
    )

    print(
        f"Records downloaded this run: "
        f"{total_records}"
    )

    print(
        f"Total completed entries: "
        f"{len(completed)}"
    )

    print(
        f"Output directory: "
        f"{OUTPUT_DIR}"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()