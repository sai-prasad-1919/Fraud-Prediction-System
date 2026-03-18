"""Create a new admin directly in MongoDB using the same schema as the app.

Usage:
    python create_mongo_admin.py --name "Sai" --email "sai@test.com" --password "Admin@123" --admin-id "Adminsai01" --role "admin"
    python create_mongo_admin.py

If --admin-id is omitted, one is auto-generated from the name.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from getpass import getpass


def get_admin_collection():
    from repositories.admin_repo import admin_collection

    return admin_collection


def get_hash_password_func():
    from utils.auth import hash_password

    return hash_password


def normalize_email(email: str) -> str:
    """Normalize and validate email format."""
    email = email.strip().lower()
    if "@" not in email or "." not in email:
        raise ValueError("Invalid email format")
    return email


def build_default_admin_id(name: str) -> str:
    """Build default admin_id in style: Admin<name>01."""
    cleaned = re.sub(r"[^a-zA-Z]", "", name).lower()
    if not cleaned:
        cleaned = "user"
    return f"Admin{cleaned}01"


def ensure_unique_admin_id(base_admin_id: str) -> str:
    """Ensure admin_id uniqueness by incrementing numeric suffix when needed."""
    admin_collection = get_admin_collection()

    if admin_collection.find_one({"admin_id": base_admin_id}) is None:
        return base_admin_id

    prefix_match = re.match(r"^(.*?)(\d+)$", base_admin_id)
    if prefix_match:
        prefix = prefix_match.group(1)
        counter = int(prefix_match.group(2))
    else:
        prefix = f"{base_admin_id}"
        counter = 1

    while True:
        counter += 1
        candidate = f"{prefix}{counter:02d}"
        if admin_collection.find_one({"admin_id": candidate}) is None:
            return candidate


def create_admin_document(
    name: str,
    email: str,
    password: str,
    admin_id: str | None = None,
    role: str = "admin",
) -> dict:
    """Create and insert an admin document in MongoDB."""
    admin_collection = get_admin_collection()
    hash_password = get_hash_password_func()

    safe_name = name.strip()
    if len(safe_name) < 2:
        raise ValueError("Name must be at least 2 characters")

    safe_email = normalize_email(email)

    if admin_collection.find_one({"email": safe_email}):
        raise ValueError(f"Admin already exists with email: {safe_email}")

    safe_password = password[:72]
    if len(safe_password) < 6:
        raise ValueError("Password must be at least 6 characters")

    safe_role = role.strip().lower() if role else "admin"
    if safe_role != "admin":
        raise ValueError("Role must be 'admin'")

    raw_admin_id = admin_id.strip() if admin_id else build_default_admin_id(safe_name)
    unique_admin_id = ensure_unique_admin_id(raw_admin_id)

    admin_data = {
        "name": safe_name,
        "email": safe_email,
        "password_hash": hash_password(safe_password),
        "created_at": datetime.utcnow(),
        "role": safe_role,
        "admin_id": unique_admin_id,
    }

    result = admin_collection.insert_one(admin_data)

    admin_data["_id"] = result.inserted_id
    return admin_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new MongoDB admin")
    parser.add_argument("--name", required=False, help="Admin full name")
    parser.add_argument("--email", required=False, help="Admin email")
    parser.add_argument("--password", required=False, help="Admin password")
    parser.add_argument("--admin-id", required=False, help="Optional explicit admin ID")
    parser.add_argument("--role", required=False, default="admin", help="Admin role (default: admin)")
    return parser


def ask_if_missing(value: str | None, label: str, secret: bool = False, optional: bool = False) -> str | None:
    if value is not None:
        return value

    prompt = f"{label}{' (optional)' if optional else ''}: "
    entered = getpass(prompt) if secret else input(prompt)

    if optional and len(entered.strip()) == 0:
        return None

    return entered


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        name = ask_if_missing(args.name, "Name")
        email = ask_if_missing(args.email, "Email")
        password = ask_if_missing(args.password, "Password", secret=True)
        admin_id = ask_if_missing(args.admin_id, "Admin ID", optional=True)
        role = ask_if_missing(args.role, "Role")

        created = create_admin_document(
            name=name,
            email=email,
            password=password,
            admin_id=admin_id,
            role=role,
        )

        print("Admin created successfully")
        print(f"_id: {created['_id']}")
        print(f"name: {created['name']}")
        print(f"email: {created['email']}")
        print(f"admin_id: {created['admin_id']}")
        print(f"role: {created['role']}")
        print(f"created_at: {created['created_at'].isoformat()}Z")
        return 0

    except ValueError as exc:
        print(f"Validation error: {exc}")
        return 1
    except Exception as exc:
        print(f"Failed to create admin: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
