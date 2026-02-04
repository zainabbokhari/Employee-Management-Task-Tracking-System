"""
Database Configuration and Session Management
Supports both SQLite (development) and MySQL (production)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Check if using SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Create database engine with appropriate configuration
if is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Check connection health before use
        pool_size=10,        # Maximum connections in pool
        max_overflow=20,     # Extra connections when pool is full
        echo=settings.DEBUG  # Log SQL statements in debug mode
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Test override support
_test_engine = None
_test_session_local = None


def set_test_engine(test_engine, test_session_local):
    """Set test engine and session for testing purposes"""
    global _test_engine, _test_session_local
    _test_engine = test_engine
    _test_session_local = test_session_local


def clear_test_engine():
    """Clear test engine override"""
    global _test_engine, _test_session_local
    _test_engine = None
    _test_session_local = None


def get_engine():
    """Get the current engine (test or production)"""
    return _test_engine if _test_engine is not None else engine


def get_session_local():
    """Get the current session local (test or production)"""
    return _test_session_local if _test_session_local is not None else SessionLocal


def get_db():
    """
    Database dependency for FastAPI routes.
    Yields a database session and ensures cleanup.
    """
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Create all tables in database - used for initial setup"""
    current_engine = get_engine()
    Base.metadata.create_all(bind=current_engine)
