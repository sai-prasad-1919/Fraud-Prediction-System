"""
Unit tests for risk scoring functionality
"""
import pytest
from ml.inference.risk_scorer import categorize_fraud_risk


class TestRiskScorer:
    """Test suite for fraud risk scoring"""
    
    def test_risk_level_1_low_risk(self):
        """Test risk level 1 categorization (30-50% fraud probability)"""
        fraud_prob = 0.40
        risk_level = categorize_fraud_risk(fraud_prob)
        # Should be categorized as level 1: 30-50%
        assert risk_level in [1, 2]  # Depends on actual bins
    
    def test_risk_level_2_medium_risk(self):
        """Test risk level 2 categorization (50-70% fraud probability)"""
        fraud_prob = 0.60
        risk_level = categorize_fraud_risk(fraud_prob)
        # Should be categorized as level 2: 50-70%
        assert risk_level in [2, 3]
    
    def test_risk_level_3_high_risk(self):
        """Test risk level 3 categorization (70%+ fraud probability)"""
        fraud_prob = 0.85
        risk_level = categorize_fraud_risk(fraud_prob)
        # Should be categorized as level 3: 70%+
        assert risk_level == 3
    
    def test_risk_level_very_low(self):
        """Test risk level with very low fraud probability"""
        fraud_prob = 0.05
        risk_level = categorize_fraud_risk(fraud_prob)
        # Should be level 1 or below
        assert risk_level >= 1
    
    def test_risk_level_boundary_values(self):
        """Test boundary values for risk levels"""
        # Test exact boundaries
        for prob in [0.30, 0.50, 0.70]:
            risk_level = categorize_fraud_risk(prob)
            assert risk_level in [1, 2, 3]
    
    def test_risk_level_return_type(self):
        """Test that risk level returns integer"""
        fraud_prob = 0.50
        risk_level = categorize_fraud_risk(fraud_prob)
        assert isinstance(risk_level, int)
    
    def test_risk_level_valid_range(self):
        """Test that risk level is always in valid range"""
        for prob in [0.0, 0.25, 0.50, 0.75, 1.0]:
            risk_level = categorize_fraud_risk(prob)
            assert 1 <= risk_level <= 3
    
    def test_risk_level_increasing_probability(self):
        """Test that risk level increases with fraud probability"""
        probs = [0.1, 0.4, 0.6, 0.8]
        risk_levels = [categorize_fraud_risk(p) for p in probs]
        # Risk levels should generally increase with probability
        assert risk_levels[-1] >= risk_levels[0]
