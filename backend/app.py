from fastapi import FastAPI
from config import settings

app = FastAPI(title=settings.APP_NAME)

@app.get("/")
def root():
    return {"status": "Backend is running", "env": settings.APP_ENV}
