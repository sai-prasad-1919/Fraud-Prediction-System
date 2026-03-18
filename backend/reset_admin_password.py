"""Reset an existing admin password in MongoDB by admin_id.

Usage:
    python reset_admin_password.py --admin-id "Akhil6785" --password "NewPass@123"
    python reset_admin_password.py
"""

from __future__ import annotations

import argparse
from getpass import getpass


def get_admin_collection():
    from repositories.admin_repo import admin_collection

    return admin_collection


def get_hash_password_func():
    from utils.auth import hash_password

    return hash_password


def ask_if_missing(value: str | None, label: str, secret: bool = False) -> str:
    if value is not None and value.strip():
        return value.strip()

    prompt = f"{label}: "
    entered = getpass(prompt) if secret else input(prompt)
    return entered.strip()


def reset_admin_password(admin_id: str, new_password: str) -> dict:
    admin_collection = get_admin_collection()
    hash_password = get_hash_password_func()

    safe_admin_id = admin_id.strip()
    if not safe_admin_id:
        raise ValueError("admin_id cannot be empty")

    safe_password = new_password[:72]
    if len(safe_password) < 6:
        raise ValueError("Password must be at least 6 characters")

    admin = admin_collection.find_one({"admin_id": safe_admin_id})
    if not admin:
        raise ValueError(f"No admin found for admin_id: {safe_admin_id}")

    new_hash = hash_password(safe_password)
    result = admin_collection.update_one(
        {"_id": admin["_id"]},
        {"$set": {"password_hash": new_hash}},
    )

    if result.modified_count != 1:
        raise RuntimeError("Password update failed")

    return {
        "admin_id": safe_admin_id,
        "email": admin.get("email", ""),
        "name": admin.get("name", ""),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reset admin password by admin_id")
    parser.add_argument("--admin-id", required=False, help="Existing admin ID")
    parser.add_argument("--password", required=False, help="New password")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        admin_id = ask_if_missing(args.admin_id, "Admin ID")
        new_password = ask_if_missing(args.password, "New password", secret=True)

        if not args.yes:
            confirm = input(f"Reset password for admin '{admin_id}'? (y/N): ").strip().lower()
            if confirm not in {"y", "yes"}:
                print("Cancelled")
                return 0

        updated = reset_admin_password(admin_id, new_password)

        print("Password updated successfully")
        print(f"admin_id: {updated['admin_id']}")
        print(f"name: {updated['name']}")
        print(f"email: {updated['email']}")
        return 0

    except ValueError as exc:
        print(f"Validation error: {exc}")
        return 1
    except Exception as exc:
        print(f"Failed to reset password: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
