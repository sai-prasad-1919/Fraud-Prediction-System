import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "Fraud Risk Backend")
    APP_ENV = os.getenv("APP_ENV", "development")

    SQL_DB_URL = os.getenv("SQL_DB_URL")
    MONGO_URL = os.getenv("MONGO_URL")

   # Debug environment variable
    print("REACT_APP_API_URL =", os.getenv("REACT_APP_API_URL"))
    
    # API Configuration
    API_BASE_URL = os.getenv("REACT_APP_API_URL", "http://localhost:8000")
    print("API_BASE_URL =", API_BASE_URL)
    
    # ML Configuration
    # Number of previous transactions to use for fraud prediction window
    # Can be 7, 8, 10 or any number you prefer
    ML_WINDOW_SIZE = int(os.getenv("ML_WINDOW_SIZE", "7"))
    
settings = Settings()
