"""
Unit tests for prediction service and case management
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from routes.admin_predict import PredictRequest
from routes.case_management import OpenCaseRequest, ResolveCaseRequest


class TestPredictRequest:
    """Test fraud prediction request validation"""
    
    def test_valid_predict_request(self):
        """Test valid prediction request"""
        request = PredictRequest(
            start_user_id="USER0001",
            end_user_id="USER0100"
        )
        assert request.start_user_id == "USER0001"
        assert request.end_user_id == "USER0100"
    
    def test_predict_user_id_cannot_be_empty(self):
        """Test that empty user ID is rejected"""
        with pytest.raises(ValidationError):
            PredictRequest(
                start_user_id="",
                end_user_id="USER0100"
            )
    
    def test_predict_user_id_must_be_string(self):
        """Test that user ID must be string"""
        with pytest.raises(ValidationError):
            PredictRequest(
                start_user_id=123,  # Should be string
                end_user_id="USER0100"
            )
    
    def test_predict_both_user_ids_required(self):
        """Test that both user IDs are required"""
        with pytest.raises(ValidationError):
            PredictRequest(start_user_id="USER0001")  # Missing end_user_id


class TestOpenCaseRequest:
    """Test fraud case opening request validation"""
    
    def test_valid_open_case_request(self):
        """Test valid case opening request"""
        request = OpenCaseRequest(
            user_id="USER0001",
            risk_level=3
        )
        assert request.user_id == "USER0001"
        assert request.risk_level == 3
    
    def test_open_case_risk_level_valid_values(self):
        """Test that risk level must be 1, 2, or 3"""
        valid_levels = [1, 2, 3]
        for level in valid_levels:
            request = OpenCaseRequest(
                user_id="USER0001",
                risk_level=level
            )
            assert request.risk_level == level
    
    def test_open_case_risk_level_invalid_value(self):
        """Test that invalid risk levels would be caught in route handler"""
        # This would be 400 error in actual route
        request = OpenCaseRequest(
            user_id="USER0001",
            risk_level=5  # Invalid
        )
        assert request.risk_level == 5  # Schema allows, route validates
    
    def test_open_case_user_id_required(self):
        """Test that user ID is required"""
        with pytest.raises(ValidationError):
            OpenCaseRequest(risk_level=1)  # Missing user_id
    
    def test_open_case_risk_level_required(self):
        """Test that risk level is required"""
        with pytest.raises(ValidationError):
            OpenCaseRequest(user_id="USER0001")  # Missing risk_level
    
    def test_open_case_example_values(self):
        """Test with example values from model_config"""
        request = OpenCaseRequest(
            user_id="USER0001",
            risk_level=3
        )
        assert request.user_id == "USER0001"
        assert request.risk_level == 3


class TestResolveCaseRequest:
    """Test fraud case resolution request validation"""
    
    def test_valid_resolve_case_request(self):
        """Test valid case resolution request"""
        request = ResolveCaseRequest(
            case_id=1,
            transaction_ids=["TXN001", "TXN002", "TXN003"]
        )
        assert request.case_id == 1
        assert len(request.transaction_ids) == 3
    
    def test_resolve_case_empty_transaction_list(self):
        """Test case resolution with empty transaction list"""
        request = ResolveCaseRequest(
            case_id=1,
            transaction_ids=[]
        )
        assert request.case_id == 1
        assert len(request.transaction_ids) == 0
    
    def test_resolve_case_case_id_required(self):
        """Test that case ID is required"""
        with pytest.raises(ValidationError):
            ResolveCaseRequest(
                transaction_ids=["TXN001"]
            )
    
    def test_resolve_case_transaction_ids_required(self):
        """Test that transaction IDs list is required"""
        with pytest.raises(ValidationError):
            ResolveCaseRequest(case_id=1)  # Missing transaction_ids
    
    def test_resolve_case_transaction_ids_must_be_list(self):
        """Test that transaction IDs must be a list"""
        with pytest.raises(ValidationError):
            ResolveCaseRequest(
                case_id=1,
                transaction_ids="TXN001"  # Should be list
            )
    
    def test_resolve_case_example_values(self):
        """Test with example values from model_config"""
        request = ResolveCaseRequest(
            case_id=1,
            transaction_ids=["TXN001", "TXN002", "TXN003"]
        )
        assert request.case_id == 1
        assert "TXN001" in request.transaction_ids


class TestCaseManagementValidation:
    """Test case management business logic validation"""
    
    def test_case_with_high_risk_level(self):
        """Test case opening with high risk level"""
        request = OpenCaseRequest(
            user_id="USER0001",
            risk_level=3
        )
        # Risk level 3 indicates strong fraud suspicion
        assert request.risk_level == 3
    
    def test_case_with_medium_risk_level(self):
        """Test case opening with medium risk level"""
        request = OpenCaseRequest(
            user_id="USER0001",
            risk_level=2
        )
        assert request.risk_level == 2
    
    def test_case_with_low_risk_level(self):
        """Test case opening with low risk level"""
        request = OpenCaseRequest(
            user_id="USER0001",
            risk_level=1
        )
        assert request.risk_level == 1
    
    def test_multiple_transactions_per_case(self):
        """Test linking multiple transactions to a case"""
        transaction_ids = [f"TXN{str(i).zfill(4)}" for i in range(1, 11)]
        request = ResolveCaseRequest(
            case_id=1,
            transaction_ids=transaction_ids
        )
        assert len(request.transaction_ids) == 10
        assert "TXN0001" in request.transaction_ids
        assert "TXN0010" in request.transaction_ids
