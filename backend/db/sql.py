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


def ensure_fraud_case_timezone_columns():
    """
    Normalize fraud case timestamp columns to TIMESTAMP WITH TIME ZONE.
    Existing naive values are treated as UTC while converting.
    """
    try:
        with engine.begin() as conn:
            table_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'fraud_cases'
                )
            """)).scalar()

            if not table_exists:
                return

            timestamp_columns = ["created_at", "investigation_started_at", "resolved_at"]

            for column_name in timestamp_columns:
                data_type = conn.execute(
                    text("""
                        SELECT data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = 'fraud_cases'
                          AND column_name = :column_name
                    """),
                    {"column_name": column_name},
                ).scalar()

                if data_type == "timestamp without time zone":
                    conn.execute(
                        text(f"""
                            ALTER TABLE fraud_cases
                            ALTER COLUMN {column_name}
                            TYPE TIMESTAMP WITH TIME ZONE
                            USING {column_name} AT TIME ZONE 'UTC'
                        """)
                    )
                    logger.info(f"Converted fraud_cases.{column_name} to TIMESTAMP WITH TIME ZONE")
    except Exception as e:
        logger.warning(f"Could not normalize fraud_cases timestamp columns: {str(e)}")

def create_tables():
    Base.metadata.create_all(bind=engine)
    ensure_fraud_case_timezone_columns()