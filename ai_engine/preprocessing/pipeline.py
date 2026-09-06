from pathlib import Path
import sys
import pandas as pd


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from ai_engine.data.validation.validator import validate_dataframe
from ai_engine.preprocessing.cleaner import clean_shipments


# ============================================================
# PREPROCESS SHIPMENT DATA
# ============================================================

def preprocess_shipments(input_file: str) -> pd.DataFrame:
    """
    Load, validate, and clean shipment data.

    Parameters
    ----------
    input_file : str
        Path to the raw shipment CSV file.

    Returns
    -------
    pd.DataFrame
        Cleaned shipment dataset.
    """

    # Load raw dataset
    df = pd.read_csv(input_file)

    print(f"Loaded records: {len(df)}")

    # --------------------------------------------------------
    # Validate dataset
    # --------------------------------------------------------

    validation_report = validate_dataframe(df)

    if not validation_report["valid"]:
        print("\n✗ Shipment dataset failed validation.")

        if validation_report["missing_columns"]:
            print(
                "\nMissing columns:",
                validation_report["missing_columns"]
            )

        if validation_report["duplicate_count"] > 0:
            print(
                "\nDuplicate shipment IDs:",
                validation_report["duplicate_count"]
            )

        if validation_report["numeric_errors"]:
            print(
                "\nNumeric errors:",
                validation_report["numeric_errors"]
            )

        if validation_report["category_errors"]:
            print(
                "\nCategory errors:",
                validation_report["category_errors"]
            )

        raise ValueError(
            "Shipment dataset failed validation."
        )

    print("✓ Validation passed.")

    # --------------------------------------------------------
    # Clean dataset
    # --------------------------------------------------------

    cleaned_df = clean_shipments(df)

    print(
        f"Records after cleaning: {len(cleaned_df)}"
    )

    return cleaned_df


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

def save_processed_data(
    df: pd.DataFrame,
    output_file: str
) -> None:
    """
    Save the cleaned shipment dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned shipment dataset.

    output_file : str
        Destination path for the processed CSV.
    """

    output_path = Path(output_file)

    # Create output directory if it does not exist
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save processed dataset
    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"✓ Processed dataset saved to: {output_path}"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("SUPPLY PRESCRIPT - SHIPMENT PREPROCESSING")
    print("=" * 70)

    # Raw dataset
    input_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "raw"
        / "shipments.csv"
    )

    # Processed dataset
    output_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "cleaned_shipments.csv"
    )

    # --------------------------------------------------------
    # Run preprocessing
    # --------------------------------------------------------

    processed_df = preprocess_shipments(
        str(input_file)
    )

    # --------------------------------------------------------
    # Save processed dataset
    # --------------------------------------------------------

    save_processed_data(
        processed_df,
        str(output_file)
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\nPreprocessing completed successfully.")
    print(
        f"Final records: {len(processed_df)}"
    )
    print(
        f"Columns: {len(processed_df.columns)}"
    )
    print(
        f"Output file: {output_file}"
    )