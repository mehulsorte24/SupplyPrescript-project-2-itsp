import csv
import os

DATA_FILE = os.path.join(
    "ai_engine",
    "data",
    "raw",
    "shipments.csv"
)

MAX_ROWS = 500_000

FIELDNAMES = [
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


def ensure_storage():
    """
    Create the raw data directory and shipment CSV
    if they do not already exist.
    """
    directory = os.path.dirname(DATA_FILE)

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES
            )
            writer.writeheader()


def get_row_count():
    """
    Return the number of shipment records currently stored.
    """
    if not os.path.exists(DATA_FILE):
        return 0

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        next(reader, None)

        return sum(1 for _ in reader)


def save_shipment(shipment):
    """
    Append one shipment record to the CSV file.

    Returns True if the shipment was saved.
    Returns False if the maximum row limit has been reached.
    """
    ensure_storage()

    current_rows = get_row_count()

    if current_rows >= MAX_ROWS:
        return False

    with open(DATA_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        writer.writerow(shipment)

    return True


def save_shipments(shipments):
    """
    Append multiple shipment records.

    Stops when the 500,000-row limit is reached.

    Returns the number of records successfully saved.
    """
    ensure_storage()

    current_rows = get_row_count()
    remaining_rows = MAX_ROWS - current_rows

    if remaining_rows <= 0:
        return 0

    shipments_to_save = shipments[:remaining_rows]

    with open(DATA_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        writer.writerows(shipments_to_save)

    return len(shipments_to_save)


if __name__ == "__main__":
    print("=" * 60)
    print("SUPPLY PRESCRIPT - STORAGE TEST")
    print("=" * 60)

    ensure_storage()

    print(f"\nData file: {DATA_FILE}")
    print(f"Current shipment records: {get_row_count()}")
    print(f"Maximum allowed records: {MAX_ROWS}")