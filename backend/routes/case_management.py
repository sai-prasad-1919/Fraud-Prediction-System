from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, update
from datetime import datetime

from db.sql import get_sql_db
from models.fraud_case import FraudCase
from models.transaction import Transaction
from utils.logger import logger

router = APIRouter(
    prefix="/admin/cases",
    tags=["Case Management"],
    responses={
        400: {"description": "Bad Request - Invalid input"},
        404: {"description": "Not Found - Case not found"},
        500: {"description": "Internal Server Error"},
    }
)


# ============ HELPER FUNCTION ============
def get_recommended_action(risk_level: int) -> str:
    """Map risk level to recommended action"""
    actions = {
        1: "KYC Review Required",
        2: "Debit Freeze & Cyber Cell Escalation",
        3: "Full Account Freeze & Immediate Investigation"
    }
    return actions.get(risk_level, "Unknown Action")




# ============ PYDANTIC MODELS ============
class CreateCaseRequest(BaseModel):
    user_id: str = Field(..., example="USER0001", description="User ID in USER#### format")
    risk_level: int = Field(..., example=3, description="Risk level: 1, 2, or 3")
    admin_id: str = Field(..., example="Adminsai01", description="Admin ID creating the case")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "USER0001",
                "risk_level": 3,
                "admin_id": "Adminsai01"
            }
        }
    }


class StartInvestigationRequest(BaseModel):
    case_id: int = Field(..., example=1, description="Case ID to investigate")
    admin_id: str = Field(..., example="Adminsai01", description="Admin starting investigation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "case_id": 1,
                "admin_id": "Adminsai01"
            }
        }
    }


class ResolveCaseRequest(BaseModel):
    case_id: int = Field(..., example=1, description="Case ID to resolve")
    resolution_reason: str = Field(..., example="False Positive - Account Verified", description="Reason for resolution")
    admin_id: str = Field(..., example="Adminsai01", description="Admin resolving the case")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "case_id": 1,
                "resolution_reason": "False Positive - Account Verified",
                "admin_id": "Adminsai01"
            }
        }
    }


class CaseResponse(BaseModel):
    id: int
    user_id: str
    risk_level: int
    recommended_action: str
    status: str
    created_by_admin_id: str
    resolved_by_admin_id: str | None
    resolution_reason: str | None
    created_at: datetime
    investigation_started_at: datetime | None
    resolved_at: datetime | None

    class Config:
        from_attributes = True


# ============ API ENDPOINTS ============

@router.post(
    "/create",
    summary="Create a new fraud case",
    description="Create a new fraud investigation case for a user with assessed risk",
    response_model=dict,
)
def create_case(request: CreateCaseRequest, db: Session = Depends(get_sql_db)):
    """
    Create a new fraud case for a user.
    
    **Request Body:**
    - **user_id**: User ID (USER#### format)
    - **risk_level**: Risk assessment level (1=KYC, 2=Debit Freeze, 3=Full Freeze)
    - **admin_id**: Admin ID creating the case
    
    **Returns:**
    - **status**: "case created"
    - **case_id**: Auto-generated case identifier
    - **case_details**: Complete case information
    """
    try:
        if request.risk_level not in [1, 2, 3]:
            logger.warning(f"Invalid risk level {request.risk_level} for user {request.user_id}")
            raise HTTPException(status_code=400, detail="Risk level must be 1, 2, or 3")
        
        logger.info(f"Creating fraud case for user {request.user_id} (Level {request.risk_level}) by admin {request.admin_id}")
        
        recommended_action = get_recommended_action(request.risk_level)
        
        case = FraudCase(
            user_id=request.user_id,
            risk_level=request.risk_level,
            recommended_action=recommended_action,
            status="OPEN",
            created_by_admin_id=request.admin_id,
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        
        logger.info(f"Fraud case {case.id} created successfully for user {request.user_id}")
        
        return {
            "status": "case created",
            "case_id": case.id,
            "user_id": case.user_id,
            "risk_level": case.risk_level,
            "recommended_action": case.recommended_action,
            "status": case.status,
            "created_by_admin_id": case.created_by_admin_id,
            "created_at": case.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating case for user {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating case: {str(e)}")


@router.put(
    "/{case_id}/investigate",
    summary="Start investigation on a case",
    description="Move a case from OPEN to UNDER_INVESTIGATION status",
    response_model=dict,
)
def start_investigation(case_id: int, request: StartInvestigationRequest, db: Session = Depends(get_sql_db)):
    """
    Start investigation on a fraud case.
    
    **Path Parameters:**
    - **case_id**: The case ID to investigate
    
    **Request Body:**
    - **admin_id**: Admin ID starting the investigation
    
    **Returns:**
    - **status**: "investigation started"
    - **case_details**: Updated case information
    """
    try:
        case = db.query(FraudCase).filter(FraudCase.id == case_id).first()
        
        if not case:
            logger.warning(f"Case {case_id} not found")
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        if case.status != "OPEN":
            logger.warning(f"Case {case_id} is not in OPEN status")
            raise HTTPException(status_code=400, detail=f"Case must be in OPEN status to start investigation")
        
        case.status = "UNDER_INVESTIGATION"
        case.investigation_started_at = datetime.utcnow()
        db.commit()
        db.refresh(case)
        
        logger.info(f"Investigation started on case {case_id} by admin {request.admin_id}")
        
        return {
            "status": "investigation started",
            "case_id": case.id,
            "user_id": case.user_id,
            "case_status": case.status,
            "investigation_started_at": case.investigation_started_at
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting investigation on case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting investigation: {str(e)}")


@router.put(
    "/{case_id}/resolve",
    summary="Resolve a fraud case",
    description="Mark a fraud case as resolved with reason and admin details",
    response_model=dict,
)
def resolve_case(case_id: int, request: ResolveCaseRequest, db: Session = Depends(get_sql_db)):
    """
    Resolve a fraud case with resolution reason.
    
    **Path Parameters:**
    - **case_id**: The case ID to resolve
    
    **Request Body:**
    - **resolution_reason**: Why the case is being resolved
    - **admin_id**: Admin ID resolving the case
    
    **Returns:**
    - **status**: "case resolved"
    - **case_details**: Updated case information
    
    **Note:** Once resolved, past transactions won't affect future predictions
    """
    try:
        case = db.query(FraudCase).filter(FraudCase.id == case_id).first()
        
        if not case:
            logger.warning(f"Case {case_id} not found")
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        if case.status == "RESOLVED":
            logger.warning(f"Case {case_id} is already resolved")
            raise HTTPException(status_code=400, detail="Case is already resolved")
        
        logger.info(f"Resolving case {case_id} by admin {request.admin_id}. Reason: {request.resolution_reason}")
        
        case.status = "RESOLVED"
        case.resolved_by_admin_id = request.admin_id
        case.resolution_reason = request.resolution_reason
        case.resolved_at = datetime.utcnow()
        
        db.commit()
        
        # ============ OPTIMIZED: FLAG TRANSACTIONS AS RESOLVED ============
        # Link transactions to case and mark as resolved (NO DATA DUPLICATION)
        # Mark transactions that existed before this case was resolved
        try:
            stmt = update(Transaction).where(
                and_(
                    Transaction.user_id == case.user_id,
                    Transaction.fraud_case_id == None,  # Only mark unlinked transactions
                    Transaction.transaction_datetime <= case.resolved_at  # Only transactions before resolution
                )
            ).values(
                fraud_case_id=case_id,
                is_resolved=True
            )
            result = db.execute(stmt)
            db.commit()
            
            affected_rows = result.rowcount
            logger.info(f"Marked {affected_rows} transactions as resolved for case {case_id} (user: {case.user_id})")
            
        except Exception as trans_err:
            db.rollback()
            logger.warning(f"Could not flag transactions as resolved: {str(trans_err)}")
        
        db.refresh(case)
        
        logger.info(f"Case {case_id} resolved successfully")
        
        return {
            "status": "case resolved",
            "case_id": case.id,
            "user_id": case.user_id,
            "case_status": case.status,
            "resolution_reason": case.resolution_reason,
            "resolved_by_admin_id": case.resolved_by_admin_id,
            "resolved_at": case.resolved_at
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error resolving case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resolving case: {str(e)}")


@router.get(
    "/list/open",
    summary="Get all open fraud cases",
    description="Retrieve all cases that are OPEN or UNDER_INVESTIGATION",
    response_model=dict,
)
def get_open_cases(db: Session = Depends(get_sql_db)):
    """
    Get all open fraud cases (not yet resolved).
    
    **Returns:**
    - **cases**: List of all open/under-investigation cases
    - **total**: Total count of open cases
    """
    try:
        cases = db.query(FraudCase).filter(
            or_(
                FraudCase.status == "OPEN",
                FraudCase.status == "UNDER_INVESTIGATION"
            )
        ).order_by(FraudCase.created_at.desc()).all()
        
        logger.info(f"Retrieved {len(cases)} open fraud cases")
        
        cases_data = [
            {
                "id": case.id,
                "user_id": case.user_id,
                "risk_level": case.risk_level,
                "recommended_action": case.recommended_action,
                "status": case.status,
                "created_by_admin_id": case.created_by_admin_id,
                "created_at": case.created_at,
                "investigation_started_at": case.investigation_started_at,
            }
            for case in cases
        ]
        
        return {
            "total": len(cases_data),
            "cases": cases_data
        }
    except Exception as e:
        logger.error(f"Error retrieving open cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving cases: {str(e)}")


@router.get(
    "/history/{user_id}",
    summary="Get case history for a user",
    description="Retrieve all past resolved cases and current open cases for a user",
    response_model=dict,
)
def get_user_case_history(user_id: str, db: Session = Depends(get_sql_db)):
    """
    Get all fraud case history for a specific user.
    
    **Path Parameters:**
    - **user_id**: User ID (USER#### format)
    
    **Returns:**
    - **open_cases**: List of currently open cases
    - **resolved_cases**: List of past resolved cases with resolution details
    - **total_cases**: Total count of all cases
    """
    try:
        open_cases = db.query(FraudCase).filter(
            and_(
                FraudCase.user_id == user_id,
                or_(
                    FraudCase.status == "OPEN",
                    FraudCase.status == "UNDER_INVESTIGATION"
                )
            )
        ).order_by(FraudCase.created_at.desc()).all()
        
        resolved_cases = db.query(FraudCase).filter(
            and_(
                FraudCase.user_id == user_id,
                FraudCase.status == "RESOLVED"
            )
        ).order_by(FraudCase.resolved_at.desc()).all()
        
        logger.info(f"Retrieved case history for user {user_id}: {len(open_cases)} open, {len(resolved_cases)} resolved")
        
        open_data = [
            {
                "id": case.id,
                "risk_level": case.risk_level,
                "recommended_action": case.recommended_action,
                "status": case.status,
                "created_by_admin_id": case.created_by_admin_id,
                "created_at": case.created_at,
            }
            for case in open_cases
        ]
        
        resolved_data = [
            {
                "id": case.id,
                "risk_level": case.risk_level,
                "recommended_action": case.recommended_action,
                "status": case.status,
                "created_by_admin_id": case.created_by_admin_id,
                "resolved_by_admin_id": case.resolved_by_admin_id,
                "resolution_reason": case.resolution_reason,
                "created_at": case.created_at,
                "resolved_at": case.resolved_at,
            }
            for case in resolved_cases
        ]
        
        return {
            "user_id": user_id,
            "open_cases": open_data,
            "resolved_cases": resolved_data,
            "total_cases": len(open_cases) + len(resolved_cases)
        }
    except Exception as e:
        logger.error(f"Error retrieving case history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving case history: {str(e)}")