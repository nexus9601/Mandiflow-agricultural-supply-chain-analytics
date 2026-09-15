import os
import pandas as pd

DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "..", "Datasets", "Cleaned", "final_integrated_dataset.csv"
)

_CACHED_DF = None

NUMERIC_COLS = [
    "arrival_quantity", "arrival_quantity_qtl", "farmer_count",
    "modal_price", "msp", "avg_temperature_c", "total_rainfall_mm",
    "avg_humidity_percent", "avg_distance_km", "avg_transit_hours",
    "avg_speed_kmph", "transit_delay_rate",
]


def get_data() -> pd.DataFrame:
    """Load and return the cleaned integrated mandi dataset."""
    global _CACHED_DF
    if _CACHED_DF is not None:
        return _CACHED_DF

    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r"([-+]?\d*\.?\d+)")[0]
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filter out empty records where primary attributes are completely null
    key_cols = [c for c in ["modal_price", "arrival_quantity_qtl"] if c in df.columns]
    if key_cols:
        df.dropna(subset=key_cols, how="all", inplace=True)

    # Impute remaining missing values for stable visualization
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col].fillna(df[col].median(), inplace=True)

    _CACHED_DF = df
    return _CACHED_DF
