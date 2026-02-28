"""
Pytest configuration and fixtures for fraud detection tests
"""
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.sql import Base
from config import settings


# ============ DATABASE FIXTURES ============

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def test_db_session_factory(test_db_engine):
    """Create test database session factory"""
    return sessionmaker(bind=test_db_engine)


@pytest.fixture
def test_db_session(test_db_session_factory):
    """Provide a test database session for each test"""
    session = test_db_session_factory()
    yield session
    session.close()


# ============ DATA FIXTURES ============

@pytest.fixture
def sample_transactions_data():
    """Create sample transaction data for testing"""
    return {
        "transaction_id": ["TXN001", "TXN002", "TXN003", "TXN004", "TXN005"],
        "user_id": ["USER0001", "USER0001", "USER0002", "USER0002", "USER0003"],
        "amount": [150.50, 200.00, 75.25, 1500.00, 50.00],
        "merchant_id": ["M001", "M002", "M001", "M003", "M001"],
        "transaction_date": pd.date_range("2024-01-01", periods=5),
        "is_fraud": [0, 0, 0, 1, 0]
    }


@pytest.fixture
def sample_transaction_df(sample_transactions_data):
    """Create a pandas DataFrame from sample transaction data"""
    return pd.DataFrame(sample_transactions_data)


@pytest.fixture
def sample_features():
    """Sample feature vector for model prediction"""
    return {
        "transaction_amount_zscore": 0.5,
        "num_transactions_last_7days": 5,
        "avg_transaction_amount": 150.0,
        "merchant_transaction_count": 10,
        "time_since_last_transaction": 2,
        "num_unique_merchants": 3,
        "max_transaction_amount": 500.0,
    }


# ============ MODEL FIXTURES ============

@pytest.fixture
def mock_xgboost_model():
    """Mock XGBoost model for testing"""
    import pickle
    from unittest.mock import MagicMock
    
    mock_model = MagicMock()
    mock_model.predict = MagicMock(return_value=[0])
    mock_model.predict_proba = MagicMock(return_value=[[0.9, 0.1]])
    return mock_model
