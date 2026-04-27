from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy.orm import Session

from db.sql import get_sql_db
from services.prediction_service import predict_user_range
from utils.logger import logger

router = APIRouter(
    prefix="/admin",
    tags=["Fraud Prediction"],
    responses={
        400: {"description": "Bad Request - Invalid user ID format"},
        500: {"description": "Internal Server Error - Prediction failed"},
    }
)


class PredictRequest(BaseModel):
    start_user_id: str = "USER0001"  # Default example for Swagger
    end_user_id: str = "USER0100"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "start_user_id": "USER0001",
                "end_user_id": "USER0100"
            }
        }
    }
    
    @field_validator('start_user_id', 'end_user_id')
    @classmethod
    def validate_user_id_format(cls, v):
        """Validate user ID format"""
        if not isinstance(v, str):
            raise ValueError("User ID must be a string")
        if len(v.strip()) == 0:
            raise ValueError("User ID cannot be empty")

        normalized = v.strip().upper()

        # Accept either "123" or "USER0123" and normalize to USER####.
        if normalized.isdigit():
            return f"USER{int(normalized):04d}"

        if normalized.startswith("USER") and normalized[4:].isdigit():
            return f"USER{int(normalized[4:]):04d}"

        raise ValueError("User ID must be numeric (e.g., '123') or USER format (e.g., 'USER0123')")

    @model_validator(mode="after")
    def validate_user_id_range(self):
        if self.start_user_id > self.end_user_id:
            raise ValueError("start_user_id must be less than or equal to end_user_id")
        return self


@router.post(
    "/predict",
    summary="Get fraud predictions for user range",
    description="Predict fraud risk for a range of users using XGBoost model",
    response_description="Predictions organized by risk level",
)
def predict_users(
    request: PredictRequest,
    db: Session = Depends(get_sql_db),
):
    """
    Get fraud predictions for a range of users.
    
    **Request Body:**
    - **start_user_id**: Starting user ID (e.g., "USER0001")
    - **end_user_id**: Ending user ID (e.g., "USER0100")
    
    **Returns:**
    - **level_1**: Users with 30-50% fraud risk
    - **level_2**: Users with 50-70% fraud risk
    - **level_3**: Users with 70%+ fraud risk
    
    **Example Response:**
    ```json
    {
        "level_1": ["USER0005", "USER0012"],
        "level_2": ["USER0023"],
        "level_3": ["USER0045", "USER0067"]
    }
    ```
    """
    try:
        logger.info(f"Prediction request received: start={request.start_user_id}, end={request.end_user_id}")
        result = predict_user_range(db, request.start_user_id, request.end_user_id)
        logger.info(f"Prediction returned with {sum(len(v) for v in result.values())} risky users")
        return result
    except ValueError as e:
        logger.warning(f"Prediction validation/data warning: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.get(
    "/predict-test",
    summary="Test prediction endpoint",
    description="Simple health check for the prediction service",
)
def predict_test():
    """
    Test endpoint to verify prediction service is operational.
    
    **Returns:**
    - **status**: "Prediction endpoint is working" if healthy
    """
    logger.debug("Prediction test endpoint called")
    return {"status": "Prediction endpoint is working"}
