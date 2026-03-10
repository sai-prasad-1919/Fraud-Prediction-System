# 🧩 Concept (Very Important)

# For each user:
# Sort transactions by time ✅ (already done)

# Slide a window of N previous transactions
# For each transaction, collect the last N transactions (including itself)

# Create:
# features (later)
# window label (later)

import pandas as pd
from datetime import timedelta


def build_rolling_windows(
    df: pd.DataFrame,
    window_size: int = 7
):
    """
    Build rolling transaction-based windows per user.
    Each window contains the last N transactions up to and including each transaction.
    
    Args:
        df: DataFrame with transactions sorted by time
        window_size: Number of previous transactions to include in each window (default: 7)
    """

    windows = []

    for user_id, user_df in df.groupby("user_id"):
        user_df = user_df.sort_values("transaction_datetime").reset_index(drop=True)

        # For each transaction (except the first window_size-1)
        for i in range(len(user_df)):
            # Get window: from max(0, i-window_size+1) to i (inclusive)
            start_idx = max(0, i - window_size + 1)
            end_idx = i + 1
            
            window_df = user_df.iloc[start_idx:end_idx].copy()

            # Ignore very small windows
            if len(window_df) < 2:
                continue

            # Use the current transaction's datetime as window end
            window_end = window_df["transaction_datetime"].iloc[-1]
            window_start = window_df["transaction_datetime"].iloc[0]

            windows.append({
                "user_id": user_id,
                "window_start": window_start,
                "window_end": window_end,
                "transactions": window_df
            })

    return windows


if __name__ == "__main__":
    from ml.data.load_data import load_transactions

    df = load_transactions("ml/data/raw/transactions_20000.csv")
    windows = build_rolling_windows(df)

    print(f"Total windows built: {len(windows)}")
    print("Sample window:")
    print(windows[0]["transactions"].head())