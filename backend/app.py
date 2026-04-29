from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from db.sql import engine
from db.mongo import mongo_db
from sqlalchemy import text
from routes.admin_routes import router as admin_router
from routes.admin_predict import router as admin_predict_router
from routes.case_management import router as case_router
from middleware.rate_limit import RateLimitMiddleware
from utils.logger import logger


# ============ FASTAPI APP WITH SWAGGER DOCUMENTATION ============
app = FastAPI(
    title=settings.APP_NAME,
    description="Fraud Detection and Prediction API with Risk Scoring",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json",  # OpenAPI schema
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Support Team",
        "email": "support@frauddetect.com",
    },
    license_info={
        "name": "MIT License",
    },
)

logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")

# Add Rate Limiting Middleware (100 requests per minute per IP)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
logger.info("Rate limiting middleware configured (100 requests/minute)")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fraud-prediction-system.onrender.com", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.
    
    Returns:
        {"status": "Backend is running"}
    """
    logger.info("Health check endpoint called")
    return {"status": "Backend is running"}

@app.get("/test-sql", tags=["Health"])
def test_sql():
    """
    Test PostgreSQL database connection.
    
    Returns:
        {"status": "SQL connected"} if connection successful
        {"status": "SQL connection failed", "error": "..."} if connection failed
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("SQL connection test: SUCCESS")
        return {"status": "SQL connected"}
    except Exception as e:
        logger.error(f"SQL connection test failed: {str(e)}")
        return {"status": "SQL connection failed", "error": str(e)}

@app.get("/test-mongo", tags=["Health"])
def test_mongo():
    """
    Test MongoDB database connection.
    
    Returns:
        {"status": "MongoDB connected"} if connection successful
        {"status": "MongoDB connection failed", "error": "..."} if connection failed
    """
    try:
        mongo_db.list_collection_names()
        logger.info("MongoDB connection test: SUCCESS")
        return {"status": "MongoDB connected"}
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {str(e)}")
        return {"status": "MongoDB connection failed", "error": str(e)}

from db.sql import create_tables

@app.on_event("startup")
def startup():
    logger.info("Application startup event triggered")
    create_tables()
    logger.info("Database tables initialized")

app.include_router(admin_router)
app.include_router(admin_predict_router)
app.include_router(case_router)

logger.info("All routers included")
