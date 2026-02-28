from sqlalchemy.orm import Session
from models.transaction import Transaction


def get_resolved_txn_ids(db: Session, user_id: str) -> set[str]:
    """
    Get all resolved transaction IDs for a user
    
    With Option 2 optimization:
    - Queries transactions table instead of resolved_transactions
    - Uses is_resolved flag and fraud_case_id to identify resolved transactions
    - No data duplication, just queries existing columns
    """
    rows = (
        db.query(Transaction.transaction_id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.is_resolved == True
        )
        .all()
    )
    return {r[0] for r in rows}