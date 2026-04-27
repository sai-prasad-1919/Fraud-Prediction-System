import json
import joblib
import pandas as pd

from ml.features.feature_engineering import compute_features
from utils.logger import logger


class RiskScorer:
    def __init__(self, model_dir: str):
        # Load model
        self.model = joblib.load(f"{model_dir}/model.pkl")

        # Load feature list
        with open(f"{model_dir}/feature_list.json", "r") as f:
            self.feature_list = json.load(f)

        logger.info(
            "RiskScorer initialized. model_dir=%s, feature_count=%s",
            model_dir,
            len(self.feature_list),
        )

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
            logger.warning("score_user called with empty user_txns dataframe")
            return None

        window_df = self.build_recent_window(
            user_txns=user_txns,
            window_size=window_size,
        )

        logger.info(
            "Feature window prepared: window_size=%s, rows=%s, cols=%s",
            window_size,
            len(window_df),
            len(window_df.columns),
        )

        required_feature_columns = [
            "amount",
            "transaction_datetime",
            "is_beneficiary",
            "counterparty_account",
            "counterparty_bank",
            "payment_type",
        ]
        missing_feature_columns = [
            col for col in required_feature_columns if col not in window_df.columns
        ]
        if missing_feature_columns:
            logger.error(
                "Missing required columns before feature engineering: %s",
                missing_feature_columns,
            )
            return None

        sample_columns = [
            col
            for col in ["transaction_id", "user_id", "amount", "transaction_datetime", "is_beneficiary"]
            if col in window_df.columns
        ]
        logger.info(
            "Feature engineering input sample: %s",
            window_df[sample_columns].head(3).to_dict(orient="records"),
        )

        features = compute_features(window_df)
        if features is None:
            logger.warning(
                "Feature engineering returned None. window_rows=%s. "
                "Likely all rows dropped due to null datetime/amount or non-positive amounts.",
                len(window_df),
            )
            return None

        logger.info(
            "Feature engineering output: feature_count=%s, sample=%s",
            len(features),
            {k: features[k] for k in list(features.keys())[:5]},
        )

        # Align feature order
        missing_model_features = [f for f in self.feature_list if f not in features]
        if missing_model_features:
            logger.error(
                "Model input shape mismatch. Missing features required by model: %s",
                missing_model_features,
            )
            return None

        X = pd.DataFrame([features])[self.feature_list]
        logger.info(
            "Model input prepared before prediction: shape=%s, columns=%s",
            X.shape,
            list(X.columns),
        )

        # Predict probability of fraud
        try:
            risk_prob = float(self.model.predict_proba(X)[0][1])
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}", exc_info=True)
            return None

        risk_pct = round(risk_prob * 100, 2)

        # Check if the last transaction is to a known beneficiary
        # If yes, reduce the risk score
        if not window_df.empty:
            last_txn = window_df.iloc[-1]  # Get the most recent transaction
            if last_txn.get('is_beneficiary', False):
                # Reduce risk by 35% if it's a known beneficiary transaction
                risk_pct = risk_pct * 0.65
                risk_pct = round(risk_pct, 2)
                logger.info(
                    "Beneficiary transaction adjustment applied. adjusted_risk_pct=%s, base_risk_pct=%s",
                    risk_pct,
                    round(risk_prob * 100, 2),
                )

        # Map to risk level
        if risk_pct >= 70:
            risk_level = 3  # Full Freeze
        elif risk_pct >= 50:
            risk_level = 2  # Debit Freeze
        elif risk_pct >= 30:
            risk_level = 1  # KYC
        else:
            logger.info(
                "Risk below threshold. risk_pct=%s, threshold=30. Returning None.",
                risk_pct,
            )
            return None  # Ignore low risk users

        logger.info(
            "Prediction successful. risk_pct=%s, risk_level=%s, window_txn_count=%s",
            risk_pct,
            risk_level,
            len(window_df),
        )

        return {
            "risk_pct": risk_pct,
            "risk_level": risk_level,
            "window_txn_count": len(window_df),
        }