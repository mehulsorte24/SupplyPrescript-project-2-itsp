import pandas as pd


REQUIRED_COLUMNS = [
    "shipment_id",
    "supplier_id",
    "origin",
    "destination",
    "transport_mode",
    "distance_km",
    "lead_time_days",
    "weather_severity",
    "traffic_level",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "priority",
    "fuel_price_index",
    "warehouse_load",
    "actual_delay_days",
    "delay_status",
    "generated_at"
]

VALID_TRANSPORT_MODES = {
    "Road",
    "Rail",
    "Air",
    "Sea"
}

VALID_WEATHER_LEVELS = {
    "Low",
    "Medium",
    "High",
    "Severe"
}

VALID_TRAFFIC_LEVELS = {
    "Low",
    "Medium",
    "High"
}

VALID_PRIORITIES = {
    "Low",
    "Medium",
    "High",
    "Critical"
}

VALID_DELAY_STATUS = {
    "ON_TIME",
    "DELAYED"
}


def validate_required_columns(df):
    """Check whether all required columns exist."""
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing_columns


def find_missing_values(df):
    """Return missing-value counts for each column."""
    return df.isnull().sum()


def find_duplicate_shipments(df):
    """Return duplicate shipment IDs."""
    return df[
        df["shipment_id"].duplicated(keep=False)
    ]


def validate_numeric_ranges(df):
    """Check shipment numerical values for invalid ranges."""
    errors = {}

    if (df["distance_km"] <= 0).any():
        errors["distance_km"] = "Distance must be greater than 0."

    if (df["lead_time_days"] <= 0).any():
        errors["lead_time_days"] = "Lead time must be greater than 0."

    if (
        (df["supplier_reliability"] < 0) |
        (df["supplier_reliability"] > 1)
    ).any():
        errors["supplier_reliability"] = (
            "Supplier reliability must be between 0 and 1."
        )

    if (df["inventory_level"] < 0).any():
        errors["inventory_level"] = (
            "Inventory level cannot be negative."
        )

    if (df["order_value"] < 0).any():
        errors["order_value"] = (
            "Order value cannot be negative."
        )

    if (df["warehouse_load"] < 0).any() | (
        df["warehouse_load"] > 1
    ).any():
        errors["warehouse_load"] = (
            "Warehouse load must be between 0 and 1."
        )

    if (df["actual_delay_days"] < 0).any():
        errors["actual_delay_days"] = (
            "Actual delay cannot be negative."
        )

    return errors


def validate_categories(df):
    """Check categorical columns against allowed values."""
    errors = {}

    invalid_transport = set(
        df.loc[
            ~df["transport_mode"].isin(VALID_TRANSPORT_MODES),
            "transport_mode"
        ].dropna()
    )

    if invalid_transport:
        errors["transport_mode"] = (
            f"Invalid values: {invalid_transport}"
        )

    invalid_weather = set(
        df.loc[
            ~df["weather_severity"].isin(VALID_WEATHER_LEVELS),
            "weather_severity"
        ].dropna()
    )

    if invalid_weather:
        errors["weather_severity"] = (
            f"Invalid values: {invalid_weather}"
        )

    invalid_traffic = set(
        df.loc[
            ~df["traffic_level"].isin(VALID_TRAFFIC_LEVELS),
            "traffic_level"
        ].dropna()
    )

    if invalid_traffic:
        errors["traffic_level"] = (
            f"Invalid values: {invalid_traffic}"
        )

    invalid_priority = set(
        df.loc[
            ~df["priority"].isin(VALID_PRIORITIES),
            "priority"
        ].dropna()
    )

    if invalid_priority:
        errors["priority"] = (
            f"Invalid values: {invalid_priority}"
        )

    invalid_status = set(
        df.loc[
            ~df["delay_status"].isin(VALID_DELAY_STATUS),
            "delay_status"
        ].dropna()
    )

    if invalid_status:
        errors["delay_status"] = (
            f"Invalid values: {invalid_status}"
        )

    return errors


def validate_dataframe(df):
    """
    Run all shipment data validation checks.
    Returns a validation report.
    """
    missing_columns = validate_required_columns(df)

    if missing_columns:
        return {
            "valid": False,
            "missing_columns": missing_columns,
            "missing_values": {},
            "duplicate_count": 0,
            "numeric_errors": {},
            "category_errors": {}
        }

    missing_values = find_missing_values(df)

    duplicate_count = df["shipment_id"].duplicated().sum()

    numeric_errors = validate_numeric_ranges(df)

    category_errors = validate_categories(df)

    has_missing_values = missing_values.sum() > 0

    valid = (
        not missing_columns
        and not has_missing_values
        and duplicate_count == 0
        and not numeric_errors
        and not category_errors
    )

    return {
        "valid": valid,
        "missing_columns": missing_columns,
        "missing_values": missing_values.to_dict(),
        "duplicate_count": int(duplicate_count),
        "numeric_errors": numeric_errors,
        "category_errors": category_errors
    }


if __name__ == "__main__":
    print("=" * 70)
    print("SUPPLY PRESCRIPT - DATA VALIDATION")
    print("=" * 70)

    data_path = "ai_engine/data/raw/shipments.csv"

    df = pd.read_csv(data_path)

    report = validate_dataframe(df)

    print(f"\nRecords checked: {len(df):,}")
    print(f"Dataset valid  : {report['valid']}")
    print(f"Duplicate IDs  : {report['duplicate_count']}")

    if report["numeric_errors"]:
        print("\nNumeric errors:")
        for error in report["numeric_errors"].values():
            print(f"- {error}")

    if report["category_errors"]:
        print("\nCategory errors:")
        for error in report["category_errors"].values():
            print(f"- {error}")

    if report["valid"]:
        print("\n✓ Shipment dataset passed validation.")
    else:
        print("\n✗ Shipment dataset contains validation issues.")