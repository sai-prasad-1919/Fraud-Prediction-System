from pymongo import MongoClient
from config import settings

client = MongoClient(settings.MONGO_URL)

mongo_db = client.get_database()
