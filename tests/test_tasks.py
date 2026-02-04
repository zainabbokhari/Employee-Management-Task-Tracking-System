"""
Tests for task endpoints
"""
import pytest
from datetime import date, timedelta


class TestTaskEndpoints:
    """Test task CRUD operations and workflow"""
    
    def test_create_task(self, client, admin_token):
        """Test creating a task"""
        response = client.post(
            "/api/tasks/",
            json={
                "title": "Complete unit tests",
                "description": "Write unit tests for all API endpoints",
                "priority": "high",
                "due_date": str(date.today() + timedelta(days=7))
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete unit tests"
        assert data["status"] == "assigned"
    
    def test_get_tasks(self, client, admin_token):
        """Test listing tasks"""
        # Create task first
        client.post(
            "/api/tasks/",
            json={
                "title": "Review code",
                "description": "Code review for PR #123"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert len(data["tasks"]) >= 1
    
    def test_get_task_by_id(self, client, admin_token):
        """Test getting a specific task"""
        # Create task
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Bug fix", "description": "Fix login bug"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        task_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Bug fix"
    
    def test_update_task(self, client, admin_token):
        """Test updating a task"""
        # Create task
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Documentation", "description": "Write API docs"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"description": "Write comprehensive API documentation", "priority": "high"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "comprehensive" in response.json()["description"]
    
    def test_update_task_status_workflow(self, client, admin_token):
        """Test task status workflow transitions"""
        # Create task
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Workflow test", "description": "Test workflow"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        task_id = create_response.json()["id"]
        
        # Valid transition: assigned -> in_progress
        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
        
        # Valid transition: in_progress -> completed
        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
    
    def test_invalid_status_transition(self, client, admin_token):
        """Test that invalid status transitions are rejected"""
        # Create task
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Invalid transition", "description": "Test invalid transition"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        task_id = create_response.json()["id"]
        
        # Invalid transition: assigned -> completed (skip in_progress)
        response = client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
    
    def test_delete_task(self, client, admin_token):
        """Test soft deleting a task"""
        # Create task
        create_response = client.post(
            "/api/tasks/",
            json={"title": "To delete", "description": "Will be deleted"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        task_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    def test_get_task_statistics(self, client, admin_token):
        """Test getting task statistics"""
        # Create some tasks
        for i in range(3):
            client.post(
                "/api/tasks/",
                json={"title": f"Stats task {i}", "description": f"Task {i}"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        response = client.get(
            "/api/tasks/stats/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "assigned" in data
        assert "completed" in data
        assert "in_progress" in data
        assert "overdue" in data
        assert data["total"] >= 3
    
    def test_filter_tasks_by_status(self, client, admin_token):
        """Test filtering tasks by status"""
        # Create task
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Filter test", "description": "Test filtering"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        task_id = create_response.json()["id"]
        
        # Move to in_progress
        client.patch(
            f"/api/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/api/tasks/?status=in_progress",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "in_progress" for task in data["tasks"])
    
    def test_filter_tasks_by_priority(self, client, admin_token):
        """Test filtering tasks by priority"""
        # Create high priority task
        client.post(
            "/api/tasks/",
            json={"title": "Urgent task", "description": "High priority", "priority": "high"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/api/tasks/?priority=high",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert all(task["priority"] == "high" for task in data["tasks"])
