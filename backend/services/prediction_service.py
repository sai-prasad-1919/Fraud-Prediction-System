from collections import defaultdict
from sqlalchemy.orm import Session

from repositories.transaction_repo import get_transactions_by_user_range
from repositories.case_repo import get_resolved_txn_ids
from ml.inference.risk_scorer import RiskScorer
from config import settings
from utils.logger import logger


risk_scorer = RiskScorer("ml/models/xgboost")


def predict_user_range(
    db: Session,
    start_user_id: str,
    end_user_id: str,
):
    logger.info(f"Prediction initiated for range: {start_user_id} to {end_user_id}")
    
    df = get_transactions_by_user_range(db, start_user_id, end_user_id)

    if df.empty:
        logger.warning(f"No transactions found for range: {start_user_id} to {end_user_id}")
        return {}

    results = defaultdict(list)

    def mask_account(account):
        """Return only last 6 digits of account number"""
        if not account:
            return "N/A"
        account_str = str(account)
        if len(account_str) <= 6:
            return account_str
        return f"****{account_str[-6:]}"

    for user_id, user_txns in df.groupby("user_id"):
        try:
            resolved_ids = get_resolved_txn_ids(db, user_id)

            if resolved_ids:
                user_txns = user_txns[~user_txns["id"].isin(resolved_ids)]

            score = risk_scorer.score_user(user_txns, window_size=settings.ML_WINDOW_SIZE)

            logger.debug(f"Scored user={user_id}, risk_pct={score.get('risk_pct') if score else None}, risk_level={score.get('risk_level') if score else None}")
            
            if score is None:
                logger.debug(f"Skipping user {user_id} - could not compute score")
                continue

            # Mask account numbers before sending to frontend
            sample_txns = user_txns.sort_values("transaction_datetime", ascending=False).head(3).to_dict(orient="records")
            for txn in sample_txns:
                if "counterparty_account" in txn:
                    txn["counterparty_account"] = mask_account(txn["counterparty_account"])

            results[f"level_{score['risk_level']}"].append({
                "user_id": user_id,
                "risk_pct": score["risk_pct"],
                "window_txn_count": score["window_txn_count"],
                "sample_transactions": sample_txns,
            })
        except Exception as e:
            logger.error(f"Error predicting for user {user_id}: {str(e)}")
            continue

    logger.info(f"Prediction completed. Found {sum(len(v) for v in results.values())} risky users")
    return results