from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)
    user_id = Column(String, index=True)  # Changed from Integer to String (USER0001, USER0002, etc.)

    transaction_datetime = Column(DateTime)

    transaction_type = Column(String)
    payment_type = Column(String)

    amount = Column(Float)
    is_beneficiary = Column(Boolean)

    location_state = Column(String)
    location_city = Column(String)

    user_bank = Column(String)
    counterparty_account = Column(String)  
    counterparty_bank = Column(String)

    label = Column(Integer)  # training only
    
    # ============ FRAUD CASE TRACKING ============
    fraud_case_id = Column(Integer, ForeignKey("fraud_cases.id"), nullable=True, index=True)
    is_resolved = Column(Boolean, default=False, index=True)