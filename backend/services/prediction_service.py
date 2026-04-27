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
        message = (
            f"No transactions found in PostgreSQL for range: {start_user_id} to {end_user_id}. "
            "Check user_id format, range values, and available data in transactions table."
        )
        logger.warning(message)
        raise ValueError(message)

    sample_columns = [
        col for col in ["transaction_id", "user_id", "amount", "transaction_datetime", "is_beneficiary"]
        if col in df.columns
    ]
    logger.info(
        "Post-fetch dataframe stats: rows=%s, cols=%s, users=%s",
        len(df),
        len(df.columns),
        df["user_id"].nunique(),
    )
    logger.info(f"Post-fetch dataframe sample: {df[sample_columns].head(3).to_dict(orient='records')}")

    results = defaultdict(list)
    diagnostics = {
        "users_seen": 0,
        "users_empty_after_resolved_filter": 0,
        "users_without_score": 0,
        "users_scored": 0,
        "user_errors": 0,
    }

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
            diagnostics["users_seen"] += 1
            original_count = len(user_txns)
            resolved_ids = get_resolved_txn_ids(db, user_id)
            resolved_count = len(resolved_ids)

            if resolved_ids:
                user_txns = user_txns[~user_txns["id"].isin(resolved_ids)]

            logger.info(
                "User pipeline stage: user_id=%s, txns_before_filter=%s, resolved_ids=%s, txns_after_filter=%s",
                user_id,
                original_count,
                resolved_count,
                len(user_txns),
            )

            if user_txns.empty:
                diagnostics["users_empty_after_resolved_filter"] += 1
                logger.warning(
                    f"User {user_id} has 0 transactions after resolved-case filtering; skipping scoring"
                )
                continue

            score = risk_scorer.score_user(user_txns, window_size=settings.ML_WINDOW_SIZE)

            logger.debug(f"Scored user={user_id}, risk_pct={score.get('risk_pct') if score else None}, risk_level={score.get('risk_level') if score else None}")
            
            if score is None:
                diagnostics["users_without_score"] += 1
                logger.debug(f"Skipping user {user_id} - could not compute score")
                continue

            diagnostics["users_scored"] += 1

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
            diagnostics["user_errors"] += 1
            logger.error(f"Error predicting for user {user_id}: {str(e)}")
            continue

    risky_users = sum(len(v) for v in results.values())

    if risky_users == 0:
        logger.warning(
            "Prediction completed with no risky users. Diagnostics=%s. "
            "Possible reasons: users filtered as resolved, features returned None, or all scores below threshold.",
            diagnostics,
        )
    else:
        logger.info(f"Prediction completed. Found {risky_users} risky users. Diagnostics={diagnostics}")

    return dict(results)