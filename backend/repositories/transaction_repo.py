from sqlalchemy.orm import Session
from models.transaction import Transaction
import pandas as pd


def get_transactions_by_user_range(
    db: Session,
    start_user_id: str,  # Changed to string for USER0001 format
    end_user_id: str,    # Changed to string for USER0001 format
):
    records = (
        db.query(Transaction)
        .filter(Transaction.user_id >= start_user_id)
        .filter(Transaction.user_id <= end_user_id)
        .all()
    )

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(
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
                "is_merchant": r.is_merchant,
                "user_bank": r.user_bank,
                "location_city": r.location_city,
                "location_state": r.location_state,
                "counterparty_account": r.counterparty_account,
                "counterparty_bank": r.counterparty_bank,
            }
            for r in records
        ]
    )