import pandas as pd

from ml.data.load_data import load_transactions
from ml.data.build_windows import build_rolling_windows
from ml.features.feature_engineering import compute_features


def build_training_dataset(csv_path: str, window_size: int = 7) -> pd.DataFrame:
    """
    Build training dataset from raw transactions.
    Each row = one N-transaction window per user.
    
    Args:
        csv_path: Path to the transactions CSV file
        window_size: Number of previous transactions to include in each window (default: 7)
    """

    df = load_transactions(csv_path)
    windows = build_rolling_windows(df, window_size=window_size)

    rows = []

    for window in windows:
        features = compute_features(window["transactions"])
        if features is None:
            continue

        # Window-level label
        label = int((window["transactions"]["label"] == 1).any())

        row = {
            "user_id": window["user_id"],
            "window_start": window["window_start"],
            "window_end": window["window_end"],
            "label": label
        }

        # Ensure all features are floats (important)
        for k, v in features.items():
            row[k] = float(v)

        rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df_train = build_training_dataset(
        "ml/data/raw/transactions_20000.csv"
    )

    print(df_train.head())
    print(df_train["label"].value_counts())
    print(df_train.info())