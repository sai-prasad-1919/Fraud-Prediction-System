import pandas as pd


def load_transactions(csv_path: str) -> pd.DataFrame:
    """
    Load transaction dataset from CSV.
    """
    df = pd.read_csv(csv_path)

    # Ensure datetime column
    df["transaction_datetime"] = pd.to_datetime(df["txn_timestamp"])

    # Convert label to numeric
    df["label"] = df["label"].map({"Fraud": 1, "Genuine": 0})

    # Column name mappings to match feature engineering expectations
    df["is_beneficiary"] = ~df["is_new_beneficiary"]  # Invert: new=False means existing beneficiary
    df["payment_type"] = df["payment_channel"]
    
    # Extract bank code from IFSC (first 4 characters)
    df["counterparty_bank"] = df["counterparty_ifsc"].str[:4]

    # Sort by time (VERY IMPORTANT)
    df = df.sort_values(["user_id", "transaction_datetime"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    
    df = load_transactions("ml/data/raw/transactions_20000.csv")
    print(df.head())
    print(df.info())