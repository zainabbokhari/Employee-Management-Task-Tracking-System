"""
CRUD Service - Generic CRUD operations and business logic
"""
from typing import Optional, List, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from datetime import date

from app.database import Base
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.employee import Employee, ProjectAssignment
from app.models.project import Project, ProjectStatus
from app.models.task import Task, TaskStatus, TaskComment
from app.utils.logger import logger, log_db_operation

# Type variable for generic CRUD
ModelType = TypeVar("ModelType", bound=Base)


class CRUDService:
    """Generic CRUD service with common operations"""
    
    @staticmethod
    def get_paginated_response(
        items: list,
        total: int,
        page: int,
        page_size: int
    ) -> dict:
        """Create paginated response"""
        total_pages = (total + page_size - 1) // page_size
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }


class DepartmentService:
    """Department CRUD operations"""
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        is_active: bool = None
    ) -> tuple[List[Department], int]:
        """Get all departments with filtering"""
        query = db.query(Department).filter(Department.is_deleted == False)
        
        if search:
            query = query.filter(
                or_(
                    Department.name.ilike(f"%{search}%"),
                    Department.code.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(Department.is_active == is_active)
        
        total = query.count()
        departments = query.offset(skip).limit(limit).all()
        
        return departments, total
    
    @staticmethod
    def get_by_id(db: Session, department_id: int) -> Optional[Department]:
        """Get department by ID"""
        return db.query(Department).filter(
            Department.id == department_id,
            Department.is_deleted == False
        ).first()
    
    @staticmethod
    def create(db: Session, department_data: dict, created_by: int = None) -> Department:
        """Create new department"""
        # Check if code already exists
        existing = db.query(Department).filter(
            Department.code == department_data.get("code")
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department code already exists"
            )
        
        department = Department(**department_data, created_by=created_by)
        db.add(department)
        db.commit()
        db.refresh(department)
        
        log_db_operation("CREATE", "departments", department.id)
        return department
    
    @staticmethod
    def update(db: Session, department_id: int, update_data: dict) -> Department:
        """Update department"""
        department = DepartmentService.get_by_id(db, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        for key, value in update_data.items():
            if value is not None:
                setattr(department, key, value)
        
        db.commit()
        db.refresh(department)
        
        log_db_operation("UPDATE", "departments", department.id)
        return department
    
    @staticmethod
    def delete(db: Session, department_id: int) -> bool:
        """Soft delete department"""
        department = DepartmentService.get_by_id(db, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if department has active employees
        employee_count = db.query(Employee).filter(
            Employee.department_id == department_id,
            Employee.is_deleted == False
        ).count()
        
        if employee_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete department with {employee_count} active employees"
            )
        
        department.is_deleted = True
        db.commit()
        
        log_db_operation("DELETE", "departments", department.id)
        return True


class EmployeeService:
    """Employee CRUD operations"""
    
    @staticmethod
    def generate_employee_code(db: Session) -> str:
        """Generate unique employee code"""
        last_employee = db.query(Employee).order_by(Employee.id.desc()).first()
        if last_employee:
            last_num = int(last_employee.employee_code.replace("EMP", ""))
            new_num = last_num + 1
        else:
            new_num = 1001
        return f"EMP{new_num}"
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        department_id: int = None,
        is_active: bool = None
    ) -> tuple[List[Employee], int]:
        """Get all employees with filtering"""
        query = db.query(Employee).filter(Employee.is_deleted == False)
        
        if search:
            query = query.filter(
                or_(
                    Employee.first_name.ilike(f"%{search}%"),
                    Employee.last_name.ilike(f"%{search}%"),
                    Employee.email.ilike(f"%{search}%"),
                    Employee.employee_code.ilike(f"%{search}%")
                )
            )
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)
        
        total = query.count()
        employees = query.offset(skip).limit(limit).all()
        
        return employees, total
    
    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        return db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.is_deleted == False
        ).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[Employee]:
        """Get employee by user ID"""
        return db.query(Employee).filter(
            Employee.user_id == user_id,
            Employee.is_deleted == False
        ).first()
    
    @staticmethod
    def create(db: Session, employee_data: dict, created_by: int = None) -> Employee:
        """Create new employee"""
        # Check if employee_code already exists
        if employee_data.get("employee_code"):
            existing_code = db.query(Employee).filter(
                Employee.employee_code == employee_data.get("employee_code")
            ).first()
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee code already exists"
                )
        
        # Check if email already exists
        existing = db.query(Employee).filter(
            Employee.email == employee_data.get("email")
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Generate employee code if not provided
        if not employee_data.get("employee_code"):
            employee_data["employee_code"] = EmployeeService.generate_employee_code(db)
        
        employee = Employee(**employee_data, created_by=created_by)
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        log_db_operation("CREATE", "employees", employee.id)
        return employee
    
    @staticmethod
    def update(db: Session, employee_id: int, update_data: dict) -> Employee:
        """Update employee"""
        employee = EmployeeService.get_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        for key, value in update_data.items():
            if value is not None:
                setattr(employee, key, value)
        
        db.commit()
        db.refresh(employee)
        
        log_db_operation("UPDATE", "employees", employee.id)
        return employee
    
    @staticmethod
    def delete(db: Session, employee_id: int) -> bool:
        """Soft delete employee"""
        employee = EmployeeService.get_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        employee.is_deleted = True
        db.commit()
        
        log_db_operation("DELETE", "employees", employee.id)
        return True


class ProjectService:
    """Project CRUD operations"""
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        department_id: int = None,
        status_filter: ProjectStatus = None,
        is_active: bool = None
    ) -> tuple[List[Project], int]:
        """Get all projects with filtering"""
        query = db.query(Project).filter(Project.is_deleted == False)
        
        if search:
            query = query.filter(
                or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.code.ilike(f"%{search}%")
                )
            )
        
        if department_id:
            query = query.filter(Project.department_id == department_id)
        
        if status_filter:
            query = query.filter(Project.status == status_filter)
        
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)
        
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        
        return projects, total
    
    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        return db.query(Project).filter(
            Project.id == project_id,
            Project.is_deleted == False
        ).first()
    
    @staticmethod
    def create(db: Session, project_data: dict, created_by: int = None) -> Project:
        """Create new project"""
        # Check if code already exists
        existing = db.query(Project).filter(
            Project.code == project_data.get("code")
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project code already exists"
            )
        
        project = Project(**project_data, created_by=created_by)
        db.add(project)
        db.commit()
        db.refresh(project)
        
        log_db_operation("CREATE", "projects", project.id)
        return project
    
    @staticmethod
    def update(db: Session, project_id: int, update_data: dict) -> Project:
        """Update project"""
        project = ProjectService.get_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)
        
        db.commit()
        db.refresh(project)
        
        log_db_operation("UPDATE", "projects", project.id)
        return project
    
    @staticmethod
    def delete(db: Session, project_id: int) -> bool:
        """Soft delete project"""
        project = ProjectService.get_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project.is_deleted = True
        db.commit()
        
        log_db_operation("DELETE", "projects", project.id)
        return True


class TaskService:
    """Task CRUD operations with workflow"""
    
    # Valid status transitions
    STATUS_TRANSITIONS = {
        TaskStatus.ASSIGNED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
        TaskStatus.IN_PROGRESS: [TaskStatus.ON_HOLD, TaskStatus.COMPLETED, TaskStatus.CANCELLED],
        TaskStatus.ON_HOLD: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
        TaskStatus.COMPLETED: [],  # Final state
        TaskStatus.CANCELLED: [],  # Final state
    }
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        project_id: int = None,
        assignee_id: int = None,
        status_filter: TaskStatus = None,
        priority: str = None
    ) -> tuple[List[Task], int]:
        """Get all tasks with filtering"""
        query = db.query(Task).filter(Task.is_deleted == False)
        
        if search:
            query = query.filter(Task.title.ilike(f"%{search}%"))
        
        if project_id:
            query = query.filter(Task.project_id == project_id)
        
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        
        if status_filter:
            query = query.filter(Task.status == status_filter)
        
        if priority:
            query = query.filter(Task.priority == priority)
        
        total = query.count()
        tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
        
        return tasks, total
    
    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        return db.query(Task).filter(
            Task.id == task_id,
            Task.is_deleted == False
        ).first()
    
    @staticmethod
    def create(db: Session, task_data: dict, created_by: int = None) -> Task:
        """Create new task"""
        task = Task(**task_data, created_by=created_by, status=TaskStatus.ASSIGNED)
        db.add(task)
        db.commit()
        db.refresh(task)
        
        log_db_operation("CREATE", "tasks", task.id)
        return task
    
    @staticmethod
    def update(db: Session, task_id: int, update_data: dict) -> Task:
        """Update task"""
        task = TaskService.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        for key, value in update_data.items():
            if value is not None:
                setattr(task, key, value)
        
        db.commit()
        db.refresh(task)
        
        log_db_operation("UPDATE", "tasks", task.id)
        return task
    
    @staticmethod
    def update_status(
        db: Session, 
        task_id: int, 
        new_status: TaskStatus, 
        user_id: int,
        comment: str = None
    ) -> Task:
        """Update task status with workflow validation"""
        task = TaskService.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Validate status transition
        allowed_transitions = TaskService.STATUS_TRANSITIONS.get(task.status, [])
        if new_status not in allowed_transitions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {task.status.value} to {new_status.value}. "
                       f"Allowed: {[s.value for s in allowed_transitions]}"
            )
        
        # Update status
        task.status = new_status
        
        # Handle status-specific logic
        if new_status == TaskStatus.IN_PROGRESS and not task.start_date:
            task.start_date = date.today()
        elif new_status == TaskStatus.COMPLETED:
            task.completed_date = date.today()
            task.progress = 100
        
        # Add comment if provided
        if comment:
            task_comment = TaskComment(
                task_id=task_id,
                user_id=user_id,
                comment=f"Status changed to {new_status.value}: {comment}"
            )
            db.add(task_comment)
        
        db.commit()
        db.refresh(task)
        
        log_db_operation("STATUS_UPDATE", "tasks", task.id, {"new_status": new_status.value})
        return task
    
    @staticmethod
    def delete(db: Session, task_id: int) -> bool:
        """Soft delete task"""
        task = TaskService.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task.is_deleted = True
        db.commit()
        
        log_db_operation("DELETE", "tasks", task.id)
        return True
    
    @staticmethod
    def get_stats(db: Session, user_id: int = None) -> dict:
        """Get task statistics"""
        query = db.query(Task).filter(Task.is_deleted == False)
        
        if user_id:
            query = query.filter(Task.assignee_id == user_id)
        
        total = query.count()
        assigned = query.filter(Task.status == TaskStatus.ASSIGNED).count()
        in_progress = query.filter(Task.status == TaskStatus.IN_PROGRESS).count()
        completed = query.filter(Task.status == TaskStatus.COMPLETED).count()
        
        # Overdue tasks
        today = date.today()
        overdue = query.filter(
            Task.due_date < today,
            Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
        ).count()
        
        return {
            "total": total,
            "assigned": assigned,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue
        }
