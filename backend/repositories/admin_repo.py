from db.mongo import mongo_db

admin_collection = mongo_db["admins"]


def create_admin(admin_data: dict):
    return admin_collection.insert_one(admin_data)


def get_admin_by_email(email: str):
    return admin_collection.find_one({"email": email})


def get_admin_by_id(admin_id: str):
    return admin_collection.find_one({"admin_id": admin_id})