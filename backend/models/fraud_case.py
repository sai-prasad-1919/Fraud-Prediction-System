from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from models.base import Base


class FraudCase(Base):
    __tablename__ = "fraud_cases"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=False)  # USER#### format
    risk_level = Column(Integer, nullable=False)  # 1, 2, or 3
    recommended_action = Column(String, nullable=False)  # KYC Review, Debit Freeze, Full Freeze
    status = Column(String, default="OPEN")  # OPEN, UNDER_INVESTIGATION, RESOLVED
    
    # Admin tracking
    created_by_admin_id = Column(String, nullable=False)  # Admin who created this case
    resolved_by_admin_id = Column(String, nullable=True)  # Admin who resolved this case
    resolution_reason = Column(Text, nullable=True)  # Why it was resolved
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)  # When case was opened
    investigation_started_at = Column(DateTime, nullable=True)  # When investigation began
    resolved_at = Column(DateTime, nullable=True)  # When case was resolved