from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


PROJECT_ROOT = Path.cwd()

NUMERIC_FEATURES = [
    "distance_km",
    "lead_time_days",
    "inventory_level",
    "supplier_reliability",
    "order_value",
    "fuel_price_index",
    "warehouse_load",
    "overall_risk_score",
]

CATEGORICAL_FEATURES = [
    "transport_mode",
    "weather_severity",
    "traffic_level",
    "priority",
]


def load_feature_data(input_file):
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {input_path}"
        )

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError(
            "Feature dataset contains no records."
        )

    return df


def prepare_features(df):
    missing_columns = [
        column
        for column in NUMERIC_FEATURES + CATEGORICAL_FEATURES
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required similarity features: "
            + ", ".join(missing_columns)
        )

    numeric_data = df[NUMERIC_FEATURES].copy()

    numeric_data = numeric_data.fillna(
        numeric_data.median(numeric_only=True)
    )

    categorical_data = pd.get_dummies(
        df[CATEGORICAL_FEATURES].astype(str),
        columns=CATEGORICAL_FEATURES
    )

    feature_matrix = pd.concat(
        [
            numeric_data.reset_index(drop=True),
            categorical_data.reset_index(drop=True),
        ],
        axis=1
    )

    scaler = StandardScaler()

    scaled_matrix = scaler.fit_transform(
        feature_matrix
    )

    return scaled_matrix, feature_matrix.columns.tolist()


def find_similar_shipments(
    df,
    shipment_index,
    n_neighbors=10
):
    if shipment_index < 0 or shipment_index >= len(df):
        raise IndexError(
            "Shipment index is outside the dataset."
        )

    if len(df) < 2:
        return []

    scaled_matrix, _ = prepare_features(df)

    neighbor_count = min(
        n_neighbors + 1,
        len(df)
    )

    model = NearestNeighbors(
        n_neighbors=neighbor_count,
        metric="euclidean"
    )

    model.fit(scaled_matrix)

    distances, indices = model.kneighbors(
        scaled_matrix[shipment_index].reshape(1, -1)
    )

    similar_shipments = []

    for distance, index in zip(
        distances[0],
        indices[0]
    ):
        if index == shipment_index:
            continue

        row = df.iloc[index]

        similarity_score = 1 / (
            1 + float(distance)
        )

        similar_shipments.append(
            {
                "shipment_id": row["shipment_id"],
                "distance": float(distance),
                "similarity_score": float(
                    similarity_score
                ),
                "delay_status": row.get(
                    "delay_status",
                    "UNKNOWN"
                ),
                "actual_delay_days": float(
                    row.get(
                        "actual_delay_days",
                        0
                    )
                ),
            }
        )

    return similar_shipments


def calculate_historical_evidence(
    similar_shipments
):
    if not similar_shipments:
        return {
            "similar_shipments": 0,
            "delayed_shipments": 0,
            "on_time_shipments": 0,
            "historical_delay_rate": 0.0,
            "average_historical_delay_days": 0.0,
        }

    delayed_shipments = [
        shipment
        for shipment in similar_shipments
        if shipment["actual_delay_days"] > 0
    ]

    total_shipments = len(
        similar_shipments
    )

    delayed_count = len(
        delayed_shipments
    )

    average_delay = sum(
        shipment["actual_delay_days"]
        for shipment in similar_shipments
    ) / total_shipments

    return {
        "similar_shipments": total_shipments,
        "delayed_shipments": delayed_count,
        "on_time_shipments": (
            total_shipments - delayed_count
        ),
        "historical_delay_rate": (
            delayed_count / total_shipments
        ),
        "average_historical_delay_days": (
            average_delay
        ),
    }


def generate_similarity_evidence(
    df,
    shipment_index,
    n_neighbors=10
):
    similar_shipments = find_similar_shipments(
        df,
        shipment_index,
        n_neighbors
    )

    evidence = calculate_historical_evidence(
        similar_shipments
    )

    shipment_id = df.iloc[
        shipment_index
    ]["shipment_id"]

    return {
        "shipment_id": shipment_id,
        "historical_evidence": evidence,
        "similar_shipments": similar_shipments,
    }


def print_similarity_report(
    results
):
    print()
    print(
        "HISTORICAL SIMILARITY ANALYSIS"
    )
    print("=" * 100)

    for result in results:
        print()
        print(
            f"Shipment: "
            f"{result['shipment_id']}"
        )

        evidence = result[
            "historical_evidence"
        ]

        print(
            f"Similar Shipments: "
            f"{evidence['similar_shipments']}"
        )

        print(
            f"Previously Delayed: "
            f"{evidence['delayed_shipments']}"
        )

        print(
            f"Previously On-Time: "
            f"{evidence['on_time_shipments']}"
        )

        print(
            f"Historical Delay Rate: "
            f"{evidence['historical_delay_rate']:.2%}"
        )

        print(
            f"Average Historical Delay: "
            f"{evidence['average_historical_delay_days']:.2f} days"
        )

        print("Closest Historical Shipments:")

        for index, shipment in enumerate(
            result["similar_shipments"][:5],
            start=1
        ):
            print(
                f"  {index}. "
                f"{shipment['shipment_id']} | "
                f"Similarity: "
                f"{shipment['similarity_score']:.3f} | "
                f"Delay: "
                f"{shipment['actual_delay_days']:.0f} days"
            )

    print()
    print("=" * 100)


def main():
    print("=" * 100)
    print(
        "SUPPLY PRESCRIPT - "
        "HISTORICAL SIMILARITY ENGINE"
    )
    print("=" * 100)

    input_file = (
        PROJECT_ROOT
        / "ai_engine"
        / "data"
        / "processed"
        / "ml_features.csv"
    )

    df = load_feature_data(
        input_file
    )

    results = []

    sample_size = min(
        10,
        len(df)
    )

    for shipment_index in range(
        sample_size
    ):
        result = generate_similarity_evidence(
            df,
            shipment_index,
            n_neighbors=10
        )

        results.append(result)

    print_similarity_report(
        results
    )

    print()
    print("=" * 100)
    print(
        "HISTORICAL SIMILARITY ENGINE COMPLETED"
    )
    print("=" * 100)


if __name__ == "__main__":
    main()
