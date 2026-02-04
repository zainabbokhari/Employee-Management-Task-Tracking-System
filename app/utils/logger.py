"""
Logging Utilities - Structured logging for the application
"""
import logging
import sys
from pythonjsonlogger import jsonlogger
from app.config import settings


def setup_logger(name: str = "employee_management") -> logging.Logger:
    """Configure and return a structured logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with JSON formatting for production
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.DEBUG:
        # Simple format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # JSON format for production
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def log_request(method: str, path: str, user_id: int = None, extra: dict = None):
    """Log API request"""
    log_data = {
        "type": "request",
        "method": method,
        "path": path,
        "user_id": user_id
    }
    if extra:
        log_data.update(extra)
    logger.info(f"API Request: {method} {path}", extra=log_data)


def log_error(error: str, exc_info: bool = False, extra: dict = None):
    """Log error"""
    log_data = {"type": "error"}
    if extra:
        log_data.update(extra)
    logger.error(error, exc_info=exc_info, extra=log_data)


def log_db_operation(operation: str, table: str, record_id: int = None, extra: dict = None):
    """Log database operation"""
    log_data = {
        "type": "db_operation",
        "operation": operation,
        "table": table,
        "record_id": record_id
    }
    if extra:
        log_data.update(extra)
    logger.info(f"DB {operation}: {table}", extra=log_data)
