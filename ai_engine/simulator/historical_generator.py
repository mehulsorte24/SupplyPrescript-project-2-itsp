from .generator import generate_shipment
from .storage import ensure_storage, save_shipments, get_row_count


DEFAULT_RECORDS = 100_000


def generate_historical_data(record_count=DEFAULT_RECORDS):
    """
    Generate historical shipment records and store them
    in the raw shipment dataset.
    """
    ensure_storage()

    existing_rows = get_row_count()
    remaining_rows = 500_000 - existing_rows

    if remaining_rows <= 0:
        print("Maximum dataset size of 500,000 records reached.")
        return 0

    records_to_generate = min(record_count, remaining_rows)

    print("=" * 70)
    print("SUPPLY PRESCRIPT - HISTORICAL DATA GENERATOR")
    print("=" * 70)

    print(f"\nExisting records : {existing_rows:,}")
    print(f"Records to create: {records_to_generate:,}")
    print(f"Maximum capacity : 500,000")

    shipments = []

    for i in range(
        existing_rows + 1,
        existing_rows + records_to_generate + 1
    ):
        shipments.append(generate_shipment(i))

    saved_count = save_shipments(shipments)

    print(f"\nSuccessfully saved: {saved_count:,} shipments")
    print(f"Total records now  : {get_row_count():,}")

    return saved_count


if __name__ == "__main__":
    generate_historical_data()
