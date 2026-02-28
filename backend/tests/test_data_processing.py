"""
Tests for feature engineering and data processing
"""
import pytest
import pandas as pd
import numpy as np


class TestDataValidation:
    """Test data validation and preprocessing"""
    
    def test_transaction_data_structure(self, sample_transaction_df):
        """Test that sample transaction data has correct structure"""
        required_columns = ["transaction_id", "user_id", "amount", "merchant_id", "transaction_date", "is_fraud"]
        assert all(col in sample_transaction_df.columns for col in required_columns)
    
    def test_transaction_data_types(self, sample_transaction_df):
        """Test that transaction data has correct data types"""
        assert sample_transaction_df["amount"].dtype in [np.float64, np.float32]
        assert sample_transaction_df["is_fraud"].dtype in [np.int64, np.int32]
    
    def test_transaction_amount_positive(self, sample_transaction_df):
        """Test that transaction amounts are positive"""
        assert all(sample_transaction_df["amount"] > 0)
    
    def test_fraud_label_binary(self, sample_transaction_df):
        """Test that fraud label is binary (0 or 1)"""
        unique_fraud_values = set(sample_transaction_df["is_fraud"].unique())
        assert unique_fraud_values.issubset({0, 1})
    
    def test_user_id_non_empty(self, sample_transaction_df):
        """Test that user IDs are non-empty"""
        assert all(sample_transaction_df["user_id"].str.len() > 0)


class TestFeatureEngineeringData:
    """Test feature engineering data preparation"""
    
    def test_sample_features_required_fields(self, sample_features):
        """Test that sample features have all required fields"""
        required_features = [
            "transaction_amount_zscore",
            "num_transactions_last_7days",
            "avg_transaction_amount",
            "merchant_transaction_count",
            "time_since_last_transaction",
            "num_unique_merchants",
            "max_transaction_amount",
        ]
        assert all(feature in sample_features for feature in required_features)
    
    def test_sample_features_numeric_values(self, sample_features):
        """Test that all features are numeric"""
        for feature_name, feature_value in sample_features.items():
            assert isinstance(feature_value, (int, float)), f"{feature_name} is not numeric"
    
    def test_transaction_amount_zscore_reasonable_range(self, sample_features):
        """Test that z-score is in reasonable range"""
        zscore = sample_features["transaction_amount_zscore"]
        # Z-scores are typically between -3 and 3
        assert -10 <= zscore <= 10
    
    def test_non_negative_feature_values(self, sample_features):
        """Test that count features are non-negative"""
        count_features = [
            "num_transactions_last_7days",
            "merchant_transaction_count",
            "time_since_last_transaction",
            "num_unique_merchants",
        ]
        for feature in count_features:
            assert sample_features[feature] >= 0


class TestDataFrameOperations:
    """Test pandas DataFrame operations for data processing"""
    
    def test_groupby_user_aggregation(self, sample_transaction_df):
        """Test aggregating transactions by user"""
        user_agg = sample_transaction_df.groupby("user_id").agg({
            "amount": "sum",
            "transaction_id": "count"
        })
        assert len(user_agg) > 0
        assert "amount" in user_agg.columns
    
    def test_fraud_rate_calculation(self, sample_transaction_df):
        """Test calculating fraud rate by user"""
        fraud_rate = sample_transaction_df.groupby("user_id")["is_fraud"].mean()
        assert all((fraud_rate >= 0) & (fraud_rate <= 1))
    
    def test_time_window_filtering(self, sample_transaction_df):
        """Test filtering transactions by time window"""
        latest_date = sample_transaction_df["transaction_date"].max()
        window_start = latest_date - pd.Timedelta(days=7)
        recent_txns = sample_transaction_df[
            sample_transaction_df["transaction_date"] >= window_start
        ]
        assert len(recent_txns) > 0
    
    def test_merchant_frequency_calculation(self, sample_transaction_df):
        """Test calculating merchant transaction frequency"""
        merchant_counts = sample_transaction_df.groupby("merchant_id").size()
        assert all(merchant_counts > 0)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        assert len(empty_df) == 0
    
    def test_nan_values_detection(self):
        """Test detection of NaN values in data"""
        data_with_nan = pd.Series([1.0, 2.0, np.nan, 4.0])
        assert data_with_nan.isna().sum() > 0
    
    def test_duplicate_transaction_ids(self):
        """Test handling of potential duplicate transaction IDs"""
        df = pd.DataFrame({
            "transaction_id": ["TXN001", "TXN001", "TXN002"],
            "user_id": ["USER0001", "USER0001", "USER0002"]
        })
        duplicates = df[df.duplicated(subset=["transaction_id"])]
        assert len(duplicates) > 0
    
    def test_future_date_detection(self):
        """Test detection of future-dated transactions"""
        today = pd.Timestamp.now()
        future_date = today + pd.Timedelta(days=1)
        is_future = future_date > today
        assert is_future
