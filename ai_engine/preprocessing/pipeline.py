import os
import sys

import pandas as pd

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_engine.data.validation.validator import validate_dataframe
from ai_engine.preprocessing.cleaner import clean_shipments


def preprocess_shipments(input_file: str) -> pd.DataFrame:
    """
    Validate and clean shipment data before model training.
    """

    # Load raw dataset
    df = pd.read_csv(input_file)

    print(f"Loaded records: {len(df)}")

    # Validate dataset
    validation_report = validate_dataframe(df)

    if not validation_report["valid"]:
        raise ValueError(
            "Shipment dataset failed validation."
        )

    print("✓ Validation passed.")

    # Clean dataset
    cleaned_df = clean_shipments(df)

    print(f"Records after cleaning: {len(cleaned_df)}")

    return cleaned_df


if __name__ == "__main__":
    input_file = "ai_engine/data/raw/shipments.csv"

    processed_df = preprocess_shipments(input_file)

    print("\nPreprocessing completed successfully.")
    print(f"Final records: {len(processed_df)}")
    print(f"Columns: {len(processed_df.columns)}")