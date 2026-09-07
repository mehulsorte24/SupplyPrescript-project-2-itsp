from pathlib import Path
import sys

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# DATASET CONFIGURATION
# ============================================================

INPUT_FILE = (
    PROJECT_ROOT
    / "ai_engine"
    / "data"
    / "processed"
    / "ml_features.csv"
)

RANDOM_STATE = 42
TEST_SIZE = 0.20


# ============================================================
# CLASSIFICATION FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "distance_km",
    "lead_time_days",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "fuel_price_index",
    "warehouse_load",
    "supplier_risk",
    "weather_risk",
    "traffic_risk",
    "inventory_risk",
    "warehouse_risk",
    "distance_risk",
    "transport_risk",
    "priority_risk",
    "fuel_pressure",
    "lead_time_pressure",
    "overall_risk_score"
]


TARGET_COLUMN = "delay_status"


# ============================================================
# TARGET ENCODING
# ============================================================

TARGET_MAPPING = {
    "ON_TIME": 0,
    "DELAYED": 1
}


# ============================================================
# LOAD DATASET
# ============================================================

def load_feature_dataset(input_file: str) -> pd.DataFrame:
    """
    Load the ML feature dataset.
    """

    df = pd.read_csv(input_file)

    print(f"Loaded records: {len(df):,}")
    print(f"Loaded columns: {len(df.columns):,}")

    return df


# ============================================================
# VALIDATE CLASSIFICATION DATA
# ============================================================

def validate_classification_data(
    df: pd.DataFrame
) -> None:
    """
    Validate that all required features and target columns
    are available for classification.
    """

    required_columns = FEATURE_COLUMNS + [
        TARGET_COLUMN
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing classification columns: "
            f"{missing_columns}"
        )

    if df[TARGET_COLUMN].isnull().any():
        raise ValueError(
            "Classification target contains missing values."
        )

    invalid_targets = set(
        df[TARGET_COLUMN].unique()
    ) - set(TARGET_MAPPING.keys())

    if invalid_targets:
        raise ValueError(
            "Invalid target values found: "
            f"{sorted(invalid_targets)}"
        )


# ============================================================
# PREPARE CLASSIFICATION DATA
# ============================================================

def prepare_classification_data(
    df: pd.DataFrame
):
    """
    Prepare feature matrix X and target vector y.

    Returns
    -------
    X : pandas.DataFrame
        ML feature matrix.

    y : pandas.Series
        Binary classification target.
    """

    validate_classification_data(df)

    # --------------------------------------------------------
    # Select features
    # --------------------------------------------------------

    X = df[FEATURE_COLUMNS].copy()

    # --------------------------------------------------------
    # Encode target
    # --------------------------------------------------------

    y = (
        df[TARGET_COLUMN]
        .map(TARGET_MAPPING)
        .astype(int)
    )

    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    missing_features = int(
        X.isnull().sum().sum()
    )

    if missing_features > 0:
        raise ValueError(
            f"Feature matrix contains "
            f"{missing_features} missing values."
        )

    return X, y


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_classification_data(
    X: pd.DataFrame,
    y: pd.Series
):
    """
    Split classification data into training and testing sets.

    Stratification is used to preserve the target distribution
    across both datasets.
    """

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y
        )
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


# ============================================================
# PRINT CLASS DISTRIBUTION
# ============================================================

def print_class_distribution(
    y: pd.Series,
    dataset_name: str
) -> None:
    """
    Print the class distribution of a target vector.
    """

    counts = y.value_counts().sort_index()

    print(f"\n{dataset_name} CLASS DISTRIBUTION")
    print("-" * 70)

    for class_value, count in counts.items():

        class_name = (
            "ON_TIME"
            if class_value == 0
            else "DELAYED"
        )

        percentage = (
            count / len(y) * 100
            if len(y) > 0
            else 0
        )

        print(
            f"{class_name:<12}: "
            f"{count:>6,} "
            f"({percentage:.2f}%)"
        )


# ============================================================
# PRINT PREPARATION REPORT
# ============================================================

def print_preparation_report(
    X: pd.DataFrame,
    y: pd.Series,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series
) -> None:
    """
    Print a complete classification dataset preparation report.
    """

    print("=" * 70)
    print("SUPPLY PRESCRIPT - CLASSIFICATION DATA PREPARATION")
    print("=" * 70)

    print("\nDATASET SUMMARY")
    print("-" * 70)

    print(
        f"Total records       : "
        f"{len(X):,}"
    )

    print(
        f"Total features      : "
        f"{len(X.columns):,}"
    )

    print(
        f"Training records    : "
        f"{len(X_train):,}"
    )

    print(
        f"Testing records     : "
        f"{len(X_test):,}"
    )

    print(
        f"Test size           : "
        f"{TEST_SIZE * 100:.0f}%"
    )

    print(
        f"Random state        : "
        f"{RANDOM_STATE}"
    )

    print("\nFEATURES")
    print("-" * 70)

    for index, column in enumerate(
        FEATURE_COLUMNS,
        start=1
    ):
        print(
            f"{index:>2}. {column}"
        )

    print("\nTARGET ENCODING")
    print("-" * 70)

    for label, value in TARGET_MAPPING.items():
        print(
            f"{label:<12} → {value}"
        )

    print_class_distribution(
        y,
        "FULL DATASET"
    )

    print_class_distribution(
        y_train,
        "TRAINING DATA"
    )

    print_class_distribution(
        y_test,
        "TESTING DATA"
    )

    print("\nDATA QUALITY")
    print("-" * 70)

    print(
        f"Training missing values : "
        f"{int(X_train.isnull().sum().sum())}"
    )

    print(
        f"Testing missing values  : "
        f"{int(X_test.isnull().sum().sum())}"
    )

    print(
        f"Training target missing : "
        f"{int(y_train.isnull().sum())}"
    )

    print(
        f"Testing target missing  : "
        f"{int(y_test.isnull().sum())}"
    )

    print("\n" + "=" * 70)
    print("CLASSIFICATION DATA PREPARATION COMPLETED")
    print("=" * 70)


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Load feature dataset
    # --------------------------------------------------------

    df = load_feature_dataset(
        str(INPUT_FILE)
    )

    # --------------------------------------------------------
    # Prepare X and y
    # --------------------------------------------------------

    X, y = prepare_classification_data(
        df
    )

    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_classification_data(
        X,
        y
    )

    # --------------------------------------------------------
    # Print report
    # --------------------------------------------------------

    print_preparation_report(
        X,
        y,
        X_train,
        X_test,
        y_train,
        y_test
    )