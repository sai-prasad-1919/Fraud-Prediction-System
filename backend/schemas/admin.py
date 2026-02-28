from pydantic import BaseModel, field_validator, Field


class AdminRegister(BaseModel):
    """Admin registration request schema"""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Admin full name (letters and spaces only)",
        example="Sai Prasad"
    )
    email: str = Field(
        ...,
        description="Admin email address",
        example="admin@frauddetect.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Admin password (minimum 6 characters)",
        example="SecurePass123"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sai Prasad",
                "email": "admin@frauddetect.com",
                "password": "SecurePass123"
            }
        }
    }
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name contains only letters and spaces"""
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError("Name must contain only letters and spaces")
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        if '@' not in v or '.' not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class AdminLogin(BaseModel):
    """Admin login request schema"""
    admin_id: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Admin ID for authentication",
        example="Adminsai01"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=72,
        description="Admin password",
        example="Admin@123"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "admin_id": "Adminsai01",
                "password": "Admin@123"
            }
        }
    }
    
    @field_validator('admin_id')
    @classmethod
    def validate_admin_id(cls, v):
        """Validate admin ID is not empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Admin ID cannot be empty")
        return v.strip()