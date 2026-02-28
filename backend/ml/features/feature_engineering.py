import pandas as pd
import numpy as np


def safe_divide(numerator, denominator):
    return numerator / denominator if denominator != 0 else 0.0


def compute_features(window_df: pd.DataFrame) -> dict | None:
    """
    Compute risk features from a 7-day transaction window.
    """

    # -------- Basic sanity cleaning --------
    df = window_df.copy()

    df = df.dropna(subset=["amount", "transaction_datetime"])
    df = df[df["amount"] > 0]

    txn_count = len(df)
    if txn_count == 0:
        return None

    # -------- Time-based features --------
    df["hour"] = df["transaction_datetime"].dt.hour
    night_txns = df[(df["hour"] >= 23) | (df["hour"] <= 2)]

    # -------- Amount-based features --------
    total_amount = df["amount"].sum()
    avg_amount = df["amount"].mean()
    max_amount = df["amount"].max()
    std_amount = df["amount"].std() if txn_count > 1 else 0.0

    rounded_txns = df[df["amount"] % 100 == 0]

    # -------- Beneficiary / counterparty features --------
    non_beneficiary_txns = df[df["is_beneficiary"] == False]
    unique_counterparties = df["counterparty_account"].nunique()

    # -------- Bank / channel features --------
    # Digital bank codes extracted from IFSC (first 4 chars)
    digital_bank_codes = ["AIRP", "JIOP", "AUBL", "IDFB"]  # Airtel, Jio, Aubank, IDFC
    digital_bank_txns = df[df["counterparty_bank"].isin(digital_bank_codes)]

    upi_txns = df[df["payment_type"] == "UPI"]

    # -------- Merchant transaction features --------
    merchant_txns = df[df["is_merchant"] == True] if "is_merchant" in df.columns else pd.DataFrame()

    # -------- Feature dictionary --------
    features = {
        "txn_count_7d": txn_count,
        "total_amount_7d": total_amount,
        "avg_amount_7d": avg_amount,
        "max_amount_7d": max_amount,
        "std_amount_7d": std_amount,

        "rounded_amount_ratio": safe_divide(len(rounded_txns), txn_count),
        "non_beneficiary_ratio": safe_divide(len(non_beneficiary_txns), txn_count),
        "night_txn_ratio": safe_divide(len(night_txns), txn_count),

        "unique_counterparties": unique_counterparties,
        "digital_bank_ratio": safe_divide(len(digital_bank_txns), txn_count),
        "upi_ratio": safe_divide(len(upi_txns), txn_count),
        "merchant_txn_ratio": safe_divide(len(merchant_txns), txn_count),
    }

    return features


if __name__ == "__main__":
    # IMPORTANT: run from backend/
    # python -m ml.features.feature_engineering

    from ml.data.load_data import load_transactions
    from ml.data.build_windows import build_rolling_windows

    # load data (path handled by caller)
    df = load_transactions("ml/data/raw/transactions_20000.csv")

    # build 7-day rolling windows
    windows = build_rolling_windows(df)

    # test on first window
    sample_features = compute_features(windows[0]["transactions"])
    print(sample_features)