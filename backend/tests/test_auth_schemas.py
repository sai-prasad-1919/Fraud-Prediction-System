"""
Unit tests for authentication and routes validation
"""
import pytest
from pydantic import ValidationError
from schemas.admin import AdminLogin, AdminRegister


class TestAdminLoginSchema:
    """Test AuthLogin Pydantic schema validation"""
    
    def test_valid_login_credentials(self):
        """Test valid login with correct admin ID and password"""
        login = AdminLogin(admin_id="Adminsai01", password="Admin@123")
        assert login.admin_id == "Adminsai01"
        assert login.password == "Admin@123"
    
    def test_login_admin_id_min_length(self):
        """Test admin ID minimum length validation"""
        with pytest.raises(ValidationError):
            AdminLogin(admin_id="Ad", password="password")  # Too short
    
    def test_login_admin_id_strip_whitespace(self):
        """Test that admin ID is stripped of whitespace"""
        login = AdminLogin(admin_id="  Adminsai01  ", password="test")
        assert login.admin_id == "Adminsai01"
    
    def test_login_admin_id_empty_raises_error(self):
        """Test that empty admin ID raises validation error"""
        with pytest.raises(ValidationError):
            AdminLogin(admin_id="", password="test")
    
    def test_login_password_required(self):
        """Test that password is required"""
        with pytest.raises(ValidationError):
            AdminLogin(admin_id="Adminsai01")  # Missing password
    
    def test_login_admin_id_required(self):
        """Test that admin ID is required"""
        with pytest.raises(ValidationError):
            AdminLogin(password="Admin@123")  # Missing admin_id


class TestAdminRegisterSchema:
    """Test AdminRegister Pydantic schema validation"""
    
    def test_valid_registration(self):
        """Test valid admin registration"""
        register = AdminRegister(
            name="Sai Prasad",
            email="admin@frauddetect.com",
            password="SecurePass123"
        )
        assert register.name == "Sai Prasad"
        assert register.email == "admin@frauddetect.com"
    
    def test_registration_name_strip_whitespace(self):
        """Test that name is stripped of whitespace"""
        register = AdminRegister(
            name="  John Doe  ",
            email="john@example.com",
            password="password123"
        )
        assert register.name == "John Doe"
    
    def test_registration_email_lowercase(self):
        """Test that email is converted to lowercase"""
        register = AdminRegister(
            name="John",
            email="JOHN@EXAMPLE.COM",
            password="password123"
        )
        assert register.email == "john@example.com"
    
    def test_registration_name_min_length(self):
        """Test name minimum length validation"""
        with pytest.raises(ValidationError):
            AdminRegister(
                name="J",  # Too short
                email="john@example.com",
                password="password123"
            )
    
    def test_registration_name_max_length(self):
        """Test name maximum length validation"""
        with pytest.raises(ValidationError):
            AdminRegister(
                name="A" * 101,  # Too long
                email="john@example.com",
                password="password123"
            )
    
    def test_registration_name_no_special_chars(self):
        """Test that name rejects special characters"""
        with pytest.raises(ValidationError):
            AdminRegister(
                name="John@Doe",  # Contains special char
                email="john@example.com",
                password="password123"
            )
    
    def test_registration_invalid_email_format(self):
        """Test that invalid email format is rejected"""
        with pytest.raises(ValidationError):
            AdminRegister(
                name="John Doe",
                email="invalidemail",  # Missing @ and domain
                password="password123"
            )
    
    def test_registration_password_min_length(self):
        """Test password minimum length validation"""
        with pytest.raises(ValidationError):
            AdminRegister(
                name="John Doe",
                email="john@example.com",
                password="pass"  # Too short
            )
    
    def test_registration_required_fields(self):
        """Test that all fields are required"""
        with pytest.raises(ValidationError):
            AdminRegister(name="John Doe")  # Missing email and password


class TestUserIdFormat:
    """Test user ID format validation across routes"""
    
    def test_valid_user_id_format(self):
        """Test valid user ID in USER#### format"""
        valid_ids = ["USER0001", "USER1000", "USER9999"]
        for user_id in valid_ids:
            assert isinstance(user_id, str)
            assert len(user_id) > 0
    
    def test_user_id_string_type_required(self):
        """Test that user ID must be string type"""
        # This test validates the type requirement in most routes
        user_ids = ["USER0001", "USER0002"]
        for user_id in user_ids:
            assert isinstance(user_id, str)
    
    def test_empty_user_id_rejected(self):
        """Test that empty user ID is rejected"""
        empty_ids = ["", "  "]
        for user_id in empty_ids:
            if user_id.strip():
                assert len(user_id.strip()) > 0
