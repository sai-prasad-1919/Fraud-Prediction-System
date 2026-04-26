import re

from repositories.admin_repo import get_admin_by_id


def build_default_admin_id(name: str) -> str:
    """Build default admin_id in style: Admin<name>01."""
    cleaned = re.sub(r"[^a-zA-Z]", "", name).lower()
    if not cleaned:
        cleaned = "user"
    return f"Admin{cleaned}01"


def ensure_unique_admin_id(base_admin_id: str) -> str:
    """Ensure admin_id uniqueness by incrementing numeric suffix when needed."""
    if get_admin_by_id(base_admin_id) is None:
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
        if get_admin_by_id(candidate) is None:
            return candidate
