import time
from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker
from config import settings
from utils.logger import logger

# ============ DATABASE CONNECTION WITH RETRY LOGIC ============

def create_engine_with_retry(database_url: str, max_retries: int = 3):
    """
    Create SQLAlchemy engine with retry logic.
    Uses exponential backoff for retries.
    
    Args:
        database_url: PostgreSQL connection URL
        max_retries: Maximum number of retry attempts
    
    Returns:
        SQLAlchemy engine
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting to connect to PostgreSQL (attempt {retry_count + 1}/{max_retries})")
            
            engine = create_engine(
                database_url,
                pool_pre_ping=True,  # Test connection before using
                pool_recycle=3600,   # Recycle connections after 1 hour
            )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("PostgreSQL connection established successfully")
            return engine
            
        except (exc.OperationalError, Exception) as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                logger.warning(f"PostgreSQL connection failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to connect to PostgreSQL after {max_retries} attempts: {str(e)}")
                raise


# Create engine with retry logic
engine = create_engine_with_retry(settings.SQL_DB_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_sql_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from models.base import Base
from models.transaction import Transaction
from models.fraud_case import FraudCase

def create_tables():
    Base.metadata.create_all(bind=engine)