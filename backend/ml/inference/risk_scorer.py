import json
import joblib
import pandas as pd
from datetime import timedelta

from ml.features.feature_engineering import compute_features


class RiskScorer:
    def __init__(self, model_dir: str):
        # Load model
        self.model = joblib.load(f"{model_dir}/model.pkl")

        # Load feature list
        with open(f"{model_dir}/feature_list.json", "r") as f:
            self.feature_list = json.load(f)

    def build_recent_window(
        self,
        user_txns: pd.DataFrame,
        reference_time: pd.Timestamp = None,
        window_size: int = 7,
    ) -> pd.DataFrame:
        """
        Take the last `window_size` transactions for a user.
        
        Args:
            user_txns: DataFrame with user's transactions sorted by time
            reference_time: Not used in N-transaction approach (kept for compatibility)
            window_size: Number of previous transactions to include (default: 7)
        """
        # Sort by datetime and take the last window_size transactions
        user_txns = user_txns.sort_values("transaction_datetime")
        window_df = user_txns.tail(window_size)
        return window_df

    def score_user(self, user_txns: pd.DataFrame, window_size: int = 7) -> dict | None:
        """
        Returns risk score and risk level for a user.
        
        Args:
            user_txns: DataFrame with user's transactions
            window_size: Number of previous transactions to consider (default: 7)
        """

        if user_txns.empty:
            return None

        window_df = self.build_recent_window(
            user_txns=user_txns,
            window_size=window_size,
        )

        features = compute_features(window_df)
        if features is None:
            return None

        # Align feature order
        X = pd.DataFrame([features])[self.feature_list]

        # Predict probability of fraud
        risk_prob = float(self.model.predict_proba(X)[0][1])
        risk_pct = round(risk_prob * 100, 2)

        # Check if the last transaction is to a known beneficiary or merchant
        # If yes, reduce the risk score
        if not window_df.empty:
            last_txn = window_df.iloc[-1]  # Get the most recent transaction
            original_risk_pct = round(risk_prob * 100, 2)
            
            # Reduce risk by 35% if it's a known beneficiary transaction
            if last_txn.get('is_beneficiary', False):
                risk_pct = risk_pct * 0.65
                risk_pct = round(risk_pct, 2)
                print(f"[BENEFICIARY] Risk reduced to {risk_pct}% (was {original_risk_pct}%)")
            
            # Reduce risk by 30% if it's a merchant payment transaction
            if last_txn.get('is_merchant', False):
                risk_pct = risk_pct * 0.70
                risk_pct = round(risk_pct, 2)
                print(f"[MERCHANT] Risk reduced to {risk_pct}% (was {original_risk_pct}%)")

        # Map to risk level
        if risk_pct >= 70:
            risk_level = 3  # Full Freeze
        elif risk_pct >= 50:
            risk_level = 2  # Debit Freeze
        elif risk_pct >= 30:
            risk_level = 1  # KYC
        else:
            return None  # Ignore low risk users

        return {
            "risk_pct": risk_pct,
            "risk_level": risk_level,
            "window_txn_count": len(window_df),
        }