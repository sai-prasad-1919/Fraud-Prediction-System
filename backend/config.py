import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "Fraud Risk Backend")
    APP_ENV = os.getenv("APP_ENV", "development")

settings = Settings()
