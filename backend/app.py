from fastapi import FastAPI
from config import settings
from db.sql import engine
from db.mongo import mongo_db
from sqlalchemy import text
from routes.admin_routes import router as admin_router

app = FastAPI(title=settings.APP_NAME)

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.get("/test-sql")
def test_sql():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "SQL connected"}

@app.get("/test-mongo")
def test_mongo():
    mongo_db.list_collection_names()
    return {"status": "MongoDB connected"}

from db.sql import create_tables

@app.on_event("startup")
def startup():
    create_tables()
    
app.include_router(admin_router)