"""
Tests for employee endpoints
"""
import pytest
from datetime import date


class TestEmployeeEndpoints:
    """Test employee CRUD operations"""
    
    def test_create_employee(self, client, admin_token):
        """Test creating an employee"""
        response = client.post(
            "/api/employees/",
            json={
                "employee_code": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "phone": "555-1234",
                "hire_date": str(date.today()),
                "designation": "Software Engineer"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["employee_code"] == "EMP001"
    
    def test_get_employees(self, client, admin_token):
        """Test listing employees"""
        # Create employee first
        client.post(
            "/api/employees/",
            json={
                "employee_code": "EMP002",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@company.com",
                "hire_date": str(date.today())
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/api/employees/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "employees" in data
        assert len(data["employees"]) >= 1
    
    def test_get_employee_by_id(self, client, admin_token):
        """Test getting a specific employee"""
        # Create employee
        create_response = client.post(
            "/api/employees/",
            json={
                "employee_code": "EMP003",
                "first_name": "Bob",
                "last_name": "Wilson",
                "email": "bob.wilson@company.com",
                "hire_date": str(date.today())
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        emp_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/employees/{emp_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Bob"
    
    def test_update_employee(self, client, admin_token):
        """Test updating an employee"""
        # Create employee
        create_response = client.post(
            "/api/employees/",
            json={
                "employee_code": "EMP004",
                "first_name": "Alice",
                "last_name": "Brown",
                "email": "alice.brown@company.com",
                "hire_date": str(date.today())
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        emp_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/employees/{emp_id}",
            json={"designation": "Senior Developer", "phone": "555-9999"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["designation"] == "Senior Developer"
    
    def test_delete_employee(self, client, admin_token):
        """Test soft deleting an employee"""
        # Create employee
        create_response = client.post(
            "/api/employees/",
            json={
                "employee_code": "EMP005",
                "first_name": "Charlie",
                "last_name": "Davis",
                "email": "charlie.davis@company.com",
                "hire_date": str(date.today())
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        emp_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/employees/{emp_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    def test_create_duplicate_employee_code(self, client, admin_token):
        """Test creating employee with duplicate code fails"""
        client.post(
            "/api/employees/",
            json={
                "employee_code": "DUP001",
                "first_name": "First",
                "last_name": "Employee",
                "email": "first@company.com",
                "hire_date": str(date.today())
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.post(
            "/api/employees/",
            json={
                "employee_code": "DUP001",
                "first_name": "Second",
                "last_name": "Employee",
                "email": "second@company.com",
                "hire_date": str(date.today())
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
    
    def test_filter_employees_by_department(self, client, admin_token):
        """Test filtering employees by department"""
        # Create department
        dept_response = client.post(
            "/api/departments/",
            json={"name": "IT", "code": "IT", "description": "IT Department"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        dept_id = dept_response.json()["id"]
        
        # Create employee in department
        client.post(
            "/api/employees/",
            json={
                "employee_code": "IT001",
                "first_name": "IT",
                "last_name": "Staff",
                "email": "it.staff@company.com",
                "hire_date": str(date.today()),
                "department_id": dept_id
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            f"/api/employees/?department_id={dept_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "employees" in data
        assert all(emp.get("department_id") == dept_id for emp in data["employees"] if emp.get("department_id"))
