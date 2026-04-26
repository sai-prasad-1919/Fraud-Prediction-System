from fastapi import APIRouter, HTTPException
from schemas.admin import AdminRegister, AdminLogin
from services.admin_service import register_admin, login_admin
from utils.logger import logger

router = APIRouter(
    prefix="/admin",
    tags=["Admin Authentication"],
    responses={
        400: {"description": "Bad Request - Invalid input data"},
        401: {"description": "Unauthorized - Invalid credentials"},
        500: {"description": "Internal Server Error"},
    }
)


@router.post(
    "/register",
    summary="Register a new admin",
    description="Create a new admin account with name, email, password, and admin_id",
    response_description="Admin registration response with admin ID and JWT token",
)
def register(data: AdminRegister):
    """
    Register a new admin user.
    
    **Request Body:**
    - **name**: Admin full name
    - **email**: Admin email address
    - **password**: Admin password (min 6 characters)
    - **admin_id**: Admin ID used for login
    
    **Returns:**
    - admin_id: Unique admin identifier
    - access_token: JWT authentication token
    - token_type: Token type (bearer)
    """
    try:
        logger.info(f"Admin registration attempt for email: {data.email}")
        result = register_admin(data)
        logger.info(f"Admin registered successfully: {data.email}")
        return result
    except Exception as e:
        logger.error(f"Admin registration failed for {data.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/login",
    summary="Admin login",
    description="Authenticate admin with Admin ID and password",
    response_description="Login response with JWT token",
)
def login(data: AdminLogin):
    """
    Admin login endpoint.
    
    **Request Body:**
    - **admin_id**: Admin ID (e.g., "Adminsai01")
    - **password**: Admin password
    
    **Returns:**
    - admin_id: Authenticated admin ID
    - token: JWT authentication token for subsequent requests
    
    **Example:**
    ```json
    {
        "admin_id": "Adminsai01",
        "password": "Admin@123"
    }
    ```
    """
    try:
        logger.info(f"Admin login attempt for ID: {data.admin_id}")
        result = login_admin(data)
        logger.info(f"Admin login successful for ID: {data.admin_id}")
        return result
    except Exception as e:
        logger.warning(f"Admin login failed for ID: {data.admin_id} - {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))