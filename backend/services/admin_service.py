from datetime import datetime
from repositories.admin_repo import create_admin, get_admin_by_email, get_admin_by_id
from utils.auth import hash_password, verify_password, create_access_token
from utils.admin_utils import ensure_unique_admin_id
from utils.logger import logger


def register_admin(data):
    """Register a new admin"""
    safe_name = data.name.strip()
    safe_email = data.email.strip().lower()

    # Check if admin already exists
    existing_admin = get_admin_by_email(safe_email)
    if existing_admin:
        logger.warning(f"Attempted registration with existing email: {safe_email}")
        raise Exception("Admin already exists with this email")
    
    safe_password = data.password[:72]
    raw_admin_id = data.admin_id.strip()
    unique_admin_id = ensure_unique_admin_id(raw_admin_id)

    admin_data = {
        "name": safe_name,
        "email": safe_email,
        "password_hash": hash_password(safe_password),
        "created_at": datetime.utcnow(),
        "role": "admin",
        "admin_id": unique_admin_id,
    }

    create_admin(admin_data)
    token = create_access_token({
        "admin_id": unique_admin_id,
        "role": "admin"
    })

    logger.info(f"New admin registered: {safe_email} with ID {unique_admin_id}")

    return {
        "message": "Admin registered successfully",
        "admin_id": unique_admin_id,
        "access_token": token,
        "token_type": "bearer",
    }


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