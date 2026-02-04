"""
Tests for authentication endpoints
"""
import pytest
from app.models.user import UserRole


class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "full_name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["full_name"] == "New User"
        assert "id" in data
    
    def test_register_duplicate_email(self, client, admin_user):
        """Test registration with existing email fails"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "admin@test.com",
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client, db_session, admin_user):
        """Test successful login"""
        db_session.commit()
        response = client.post(
            "/api/auth/token",
            data={"username": "admin@test.com", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, db_session, admin_user):
        """Test login with wrong password"""
        db_session.commit()
        response = client.post(
            "/api/auth/token",
            data={"username": "admin@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/token",
            data={"username": "nonexistent@test.com", "password": "password123"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, admin_token):
        """Test getting current user info"""
        print(f"Token: {admin_token[:50]}...")  # Debug
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Response: {response.status_code}, {response.json()}")  # Debug
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_can_access_admin_endpoint(self, client, admin_token):
        """Test admin can access admin-only endpoints"""
        response = client.get(
            "/api/departments/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    def test_manager_can_access_manager_endpoint(self, client, manager_token):
        """Test manager can access manager endpoints"""
        response = client.get(
            "/api/departments/",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
    
    def test_employee_can_access_protected_endpoint(self, client, employee_token):
        """Test employee can access general protected endpoints"""
        response = client.get(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
