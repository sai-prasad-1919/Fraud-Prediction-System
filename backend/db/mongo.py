import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from config import settings
from utils.logger import logger

# ============ MONGODB CONNECTION WITH RETRY LOGIC ============

def create_mongo_client_with_retry(mongo_url: str, max_retries: int = 3):
    """
    Create MongoDB client with retry logic.
    Uses exponential backoff for retries.
    
    Args:
        mongo_url: MongoDB connection URL
        max_retries: Maximum number of retry attempts
    
    Returns:
        MongoDB client
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting to connect to MongoDB (attempt {retry_count + 1}/{max_retries})")
            
            client = MongoClient(
                mongo_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,
                retryWrites=True,
            )
            
            # Test the connection
            client.admin.command('ping')
            
            logger.info("MongoDB connection established successfully")
            return client
            
        except (ServerSelectionTimeoutError, ConnectionFailure, Exception) as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                logger.warning(f"MongoDB connection failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to connect to MongoDB after {max_retries} attempts: {str(e)}")
                raise


# Create client with retry logic
client = create_mongo_client_with_retry(settings.MONGO_URL)

mongo_db = client.get_database()

logger.info("MongoDB client initialized")
