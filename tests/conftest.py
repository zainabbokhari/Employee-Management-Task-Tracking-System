"""
Test configuration and fixtures
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database utilities first to set up test engine before app import
from app.database import Base, set_test_engine, clear_test_engine, get_db

# Import all models to register them with Base metadata
from app.models import User, Department, Employee, Project, Task

from app.models.user import UserRole
from app.services.auth import AuthService
from app.schemas.user import UserCreate

# Global test database variables
_test_db_path = None
_test_engine = None
_TestingSessionLocal = None


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Create tables before each test and clean up after"""
    global _test_db_path, _test_engine, _TestingSessionLocal
    
    # Create a temporary database file
    fd, _test_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Create engine
    _test_engine = create_engine(
        f"sqlite:///{_test_db_path}",
        connect_args={"check_same_thread": False},
    )
    _TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)
    
    # Set the test engine BEFORE importing app (so lifespan uses test DB)
    set_test_engine(_test_engine, _TestingSessionLocal)
    
    # Create tables
    Base.metadata.create_all(bind=_test_engine)
    
    yield
    
    # Clear test engine override
    clear_test_engine()
    
    # Cleanup
    if _test_db_path and os.path.exists(_test_db_path):
        try:
            os.remove(_test_db_path)
        except:
            pass


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    """Get database session for test"""
    global _TestingSessionLocal
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session override"""
    # Import app here to ensure test engine is set
    from app.main import app
    
    # Don't raise server exceptions so we can check error responses
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create admin user for testing"""
    user_data = UserCreate(
        email="admin@test.com",
        password="admin123",
        full_name="Test Admin",
        role=UserRole.ADMIN
    )
    user = AuthService.create_user(db_session, user_data)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def manager_user(db_session):
    """Create manager user for testing"""
    user_data = UserCreate(
        email="manager@test.com",
        password="manager123",
        full_name="Test Manager",
        role=UserRole.MANAGER
    )
    user = AuthService.create_user(db_session, user_data)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def employee_user(db_session):
    """Create employee user for testing"""
    user_data = UserCreate(
        email="employee@test.com",
        password="employee123",
        full_name="Test Employee",
        role=UserRole.EMPLOYEE
    )
    user = AuthService.create_user(db_session, user_data)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Get admin authentication token"""
    response = client.post(
        "/api/auth/token",
        data={"username": "admin@test.com", "password": "admin123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def manager_token(client, manager_user):
    """Get manager authentication token"""
    response = client.post(
        "/api/auth/token",
        data={"username": "manager@test.com", "password": "manager123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def employee_token(client, employee_user):
    """Get employee authentication token"""
    response = client.post(
        "/api/auth/token",
        data={"username": "employee@test.com", "password": "employee123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]
