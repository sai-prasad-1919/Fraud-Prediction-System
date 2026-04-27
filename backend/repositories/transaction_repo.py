from sqlalchemy.orm import Session
from models.transaction import Transaction
import pandas as pd
from utils.logger import logger


def get_transactions_by_user_range(
    db: Session,
    start_user_id: str,  # Changed to string for USER0001 format
    end_user_id: str,    # Changed to string for USER0001 format
):
    logger.info(f"SQL fetch start: start_user_id={start_user_id}, end_user_id={end_user_id}")

    records = (
        db.query(Transaction)
        .filter(Transaction.user_id >= start_user_id)
        .filter(Transaction.user_id <= end_user_id)
        .all()
    )

    if not records:
        logger.warning(
            f"SQL fetch returned 0 rows for range start_user_id={start_user_id}, end_user_id={end_user_id}"
        )
        return pd.DataFrame()

    df = pd.DataFrame(
        [
            {
                "id": r.transaction_id,  # Added transaction_id as "id" for filtering
                "transaction_id": r.transaction_id,
                "user_id": r.user_id,
                "amount": r.amount,
                "transaction_datetime": r.transaction_datetime,
                "transaction_type": r.transaction_type,
                "payment_type": r.payment_type,
                "is_beneficiary": r.is_beneficiary,
                "user_bank": r.user_bank,
                "location_city": r.location_city,
                "location_state": r.location_state,
                "counterparty_account": r.counterparty_account,
                "counterparty_bank": r.counterparty_bank,
            }
            for r in records
        ]
    )

    # Ensure datetime dtype for downstream .dt feature extraction.
    df["transaction_datetime"] = pd.to_datetime(df["transaction_datetime"], errors="coerce")

    sample_columns = [
        col for col in ["transaction_id", "user_id", "amount", "transaction_datetime", "is_beneficiary"]
        if col in df.columns
    ]
    sample_rows = df[sample_columns].head(3).to_dict(orient="records")

    logger.info(
        "SQL fetch complete: rows=%s, unique_users=%s, null_transaction_datetime=%s",
        len(df),
        df["user_id"].nunique(),
        int(df["transaction_datetime"].isna().sum()),
    )
    logger.info(f"SQL fetch sample rows: {sample_rows}")

    return df