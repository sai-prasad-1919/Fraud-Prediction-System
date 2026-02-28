import logging
import logging.handlers
import os
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logging(app_name: str = "fraud_prediction"):
    """
    Setup logging configuration with both file and console handlers.
    
    Args:
        app_name: Name of the application for log files
    """
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    
    # File handler (rotating log files)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / f"{app_name}.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Get logger instance
logger = logging.getLogger("fraud_prediction")

if not logger.handlers:
    logger = setup_logging()
