"""Feature names and bounds shared by training and inference (dataset columns only)."""

NUMERIC_FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]
TARGET_COLUMN = "label"

FEATURE_BOUNDS: dict[str, tuple[float, float]] = {
    "N": (0, 150),
    "P": (0, 150),
    "K": (0, 210),
    "temperature": (0, 50),
    "humidity": (0, 100),
    "ph": (0, 14),
    "rainfall": (0, 400),
}
