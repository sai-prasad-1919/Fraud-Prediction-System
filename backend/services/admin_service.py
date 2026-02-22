from datetime import datetime
from repositories.admin_repo import create_admin, get_admin_by_email
from utils.auth import hash_password, verify_password, create_access_token


def register_admin(data):
    # Check if admin already exists
    existing_admin = get_admin_by_email(data.email)
    if existing_admin:
        raise Exception("Admin already exists")
    
    safe_password = data.password[:72]

    admin_data = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(safe_password),
        "created_at": datetime.utcnow(),
        "role": "admin"
    }

    create_admin(admin_data)

    return {"message": "Admin registered successfully"}


def login_admin(data):
    admin = get_admin_by_email(data.email)

    if not admin:
        raise Exception("Invalid email or password")

    if not verify_password(data.password, admin["password_hash"]):
        raise Exception("Invalid email or password")

    token = create_access_token({
        "email": admin["email"],
        "role": admin["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }