from datetime import datetime
from repositories.admin_repo import create_admin, get_admin_by_email, get_admin_by_id
from utils.auth import hash_password, verify_password, create_access_token
from utils.logger import logger


def register_admin(data):
    """Register a new admin"""
    # Check if admin already exists
    existing_admin = get_admin_by_email(data.email)
    if existing_admin:
        logger.warning(f"Attempted registration with existing email: {data.email}")
        raise Exception("Admin already exists with this email")
    
    safe_password = data.password[:72]

    admin_data = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(safe_password),
        "created_at": datetime.utcnow(),
        "role": "admin"
    }

    result = create_admin(admin_data)
    logger.info(f"New admin registered: {data.email}")

    return {"message": "Admin registered successfully"}


def login_admin(data):
    """Authenticate admin and return JWT token"""
    admin = get_admin_by_id(data.admin_id)

    if not admin:
        logger.warning(f"Login attempt with non-existent admin ID: {data.admin_id}")
        raise Exception("Invalid Admin ID or password")

    if not verify_password(data.password, admin["password_hash"]):
        logger.warning(f"Login attempt with wrong password for admin ID: {data.admin_id}")
        raise Exception("Invalid Admin ID or password")

    token = create_access_token({
        "admin_id": admin.get("admin_id", admin["email"]),
        "role": admin["role"]
    })

    logger.info(f"Admin login successful: {data.admin_id}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }