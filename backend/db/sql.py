from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.SQL_DB_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_sql_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from models.base import Base
from models.transaction import Transaction
from models.resolution import TransactionResolution
from models.fraud_score import FraudScore
from models.audit_log import AdminAuditLog

def create_tables():
    Base.metadata.create_all(bind=engine)