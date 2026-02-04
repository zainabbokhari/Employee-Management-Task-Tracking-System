"""
Tests for department endpoints
"""
import pytest


class TestDepartmentEndpoints:
    """Test department CRUD operations"""
    
    def test_create_department(self, client, admin_token):
        """Test creating a department"""
        response = client.post(
            "/api/departments/",
            json={
                "name": "Engineering",
                "code": "ENG",
                "description": "Software Engineering Department"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Engineering"
        assert data["code"] == "ENG"
        assert "id" in data
    
    def test_get_departments(self, client, admin_token):
        """Test listing departments"""
        # Create a department first
        client.post(
            "/api/departments/",
            json={"name": "HR", "code": "HR", "description": "Human Resources"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/api/departments/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "departments" in data
        assert len(data["departments"]) >= 1
    
    def test_get_department_by_id(self, client, admin_token):
        """Test getting a specific department"""
        # Create department
        create_response = client.post(
            "/api/departments/",
            json={"name": "Finance", "code": "FIN", "description": "Finance Department"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        dept_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/departments/{dept_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Finance"
    
    def test_update_department(self, client, admin_token):
        """Test updating a department"""
        # Create department
        create_response = client.post(
            "/api/departments/",
            json={"name": "Marketing", "code": "MKT", "description": "Marketing"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        dept_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/departments/{dept_id}",
            json={"name": "Digital Marketing", "description": "Digital Marketing Team"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Digital Marketing"
    
    def test_delete_department(self, client, admin_token):
        """Test soft deleting a department"""
        # Create department
        create_response = client.post(
            "/api/departments/",
            json={"name": "Temp", "code": "TMP", "description": "Temporary"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        dept_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/departments/{dept_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Verify it's deleted (soft delete)
        get_response = client.get(
            f"/api/departments/{dept_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404
    
    def test_create_duplicate_department_code(self, client, admin_token):
        """Test creating department with duplicate code fails"""
        client.post(
            "/api/departments/",
            json={"name": "Sales", "code": "SAL", "description": "Sales"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.post(
            "/api/departments/",
            json={"name": "Sales 2", "code": "SAL", "description": "Another Sales"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
    
    def test_employee_cannot_create_department(self, client, employee_token):
        """Test that employees cannot create departments"""
        response = client.post(
            "/api/departments/",
            json={"name": "Test", "code": "TST", "description": "Test"},
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 403
