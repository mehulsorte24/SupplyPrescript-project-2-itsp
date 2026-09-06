import pandas as pd


NUMERIC_COLUMNS = [
    "distance_km",
    "lead_time_days",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "fuel_price_index",
    "warehouse_load",
    "actual_delay_days",
]

CATEGORICAL_COLUMNS = [
    "supplier_id",
    "origin",
    "destination",
    "transport_mode",
    "weather_severity",
    "traffic_level",
    "priority",
]


def clean_shipments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean shipment data before feature engineering and model training.
    """

    cleaned_df = df.copy()

    # Remove completely empty rows
    cleaned_df = cleaned_df.dropna(how="all")

    # Remove duplicate shipment records
    if "shipment_id" in cleaned_df.columns:
        cleaned_df = cleaned_df.drop_duplicates(
            subset=["shipment_id"],
            keep="first"
        )

    # Convert numeric columns to numeric values
    for column in NUMERIC_COLUMNS:
        if column in cleaned_df.columns:
            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

    # Clean categorical text values
    for column in CATEGORICAL_COLUMNS:
        if column in cleaned_df.columns:
            cleaned_df[column] = (
                cleaned_df[column]
                .astype("string")
                .str.strip()
            )

    # Remove records with missing critical fields
    critical_columns = [
        "shipment_id",
        "supplier_id",
        "origin",
        "destination",
        "transport_mode",
        "lead_time_days",
        "supplier_reliability",
        "delay_status",
    ]

    existing_critical_columns = [
        column
        for column in critical_columns
        if column in cleaned_df.columns
    ]

    cleaned_df = cleaned_df.dropna(
        subset=existing_critical_columns
    )

    # Keep numeric values within valid ranges
    if "supplier_reliability" in cleaned_df.columns:
        cleaned_df = cleaned_df[
            cleaned_df["supplier_reliability"].between(0, 1)
        ]

    if "warehouse_load" in cleaned_df.columns:
        cleaned_df = cleaned_df[
            cleaned_df["warehouse_load"].between(0, 1)
        ]

    if "distance_km" in cleaned_df.columns:
        cleaned_df = cleaned_df[
            cleaned_df["distance_km"] > 0
        ]

    if "lead_time_days" in cleaned_df.columns:
        cleaned_df = cleaned_df[
            cleaned_df["lead_time_days"] > 0
        ]

    # Reset index after cleaning
    cleaned_df = cleaned_df.reset_index(drop=True)

    return cleaned_df


if __name__ == "__main__":
    input_file = "ai_engine/data/raw/shipments.csv"

    df = pd.read_csv(input_file)

    print(f"Records before cleaning: {len(df)}")

    cleaned = clean_shipments(df)

    print(f"Records after cleaning : {len(cleaned)}")
    print(f"Records removed        : {len(df) - len(cleaned)}")