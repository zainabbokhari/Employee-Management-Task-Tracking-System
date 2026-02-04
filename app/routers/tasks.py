"""
Task Router - CRUD endpoints for tasks with workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskStats
)
from app.models.task import TaskStatus, TaskPriority
from app.services.crud import TaskService, EmployeeService
from app.utils.security import get_current_user, require_admin, require_manager_or_admin
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.employee import Employee

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by title"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    my_tasks: bool = Query(False, description="Show only my tasks"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks with pagination and filtering.
    
    - **Admin/Manager**: Can see all tasks
    - **Employee**: Can see only assigned tasks (or use my_tasks=true)
    """
    # Role-based filtering
    if current_user.role == UserRole.EMPLOYEE or my_tasks:
        employee = EmployeeService.get_by_user_id(db, current_user.id)
        if employee:
            assignee_id = employee.id
        else:
            return TaskListResponse(
                tasks=[],
                total=0,
                page=1,
                page_size=page_size,
                total_pages=0
            )
    
    skip = (page - 1) * page_size
    tasks, total = TaskService.get_all(
        db, 
        skip=skip, 
        limit=page_size, 
        search=search, 
        project_id=project_id,
        assignee_id=assignee_id,
        status_filter=status_filter,
        priority=priority.value if priority else None
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/stats", response_model=TaskStats)
async def get_task_stats(
    my_stats: bool = Query(False, description="Show only my stats"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get task statistics.
    
    - **my_stats=true**: Get stats for current user's tasks only
    """
    user_id = None
    if my_stats or current_user.role == UserRole.EMPLOYEE:
        employee = EmployeeService.get_by_user_id(db, current_user.id)
        if employee:
            user_id = employee.id
    
    return TaskService.get_stats(db, user_id)


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get task details by ID.
    """
    task = TaskService.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Role-based access check for employees
    if current_user.role == UserRole.EMPLOYEE:
        employee = EmployeeService.get_by_user_id(db, current_user.id)
        if not employee or task.assignee_id != employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Get project name
    project_name = None
    if task.project_id:
        project = db.query(Project).filter(Project.id == task.project_id).first()
        if project:
            project_name = project.name
    
    # Get assignee name
    assignee_name = None
    if task.assignee_id:
        assignee = db.query(Employee).filter(Employee.id == task.assignee_id).first()
        if assignee:
            assignee_name = f"{assignee.first_name} {assignee.last_name}"
    
    # Get creator name
    created_by_name = None
    if task.created_by:
        creator = db.query(User).filter(User.id == task.created_by).first()
        if creator:
            created_by_name = creator.full_name
    
    return TaskDetailResponse(
        **task.__dict__,
        project_name=project_name,
        assignee_name=assignee_name,
        created_by_name=created_by_name
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Create a new task.
    
    **Admin/Manager only**
    
    - **title**: Task title
    - **description**: Task description
    - **project_id**: Associated project
    - **assignee_id**: Employee to assign
    - **priority**: Task priority (default: medium)
    - **due_date**: Task due date
    """
    return TaskService.create(
        db, 
        task_data.model_dump(exclude_unset=True),
        created_by=current_user.id
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update task information.
    
    - **Admin/Manager**: Can update any task
    - **Employee**: Can only update progress and hours on assigned tasks
    """
    task = TaskService.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Role-based access check
    if current_user.role == UserRole.EMPLOYEE:
        employee = EmployeeService.get_by_user_id(db, current_user.id)
        if not employee or task.assignee_id != employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Employees can only update limited fields
        allowed_fields = {"progress", "actual_hours"}
        update_data = {k: v for k, v in task_data.model_dump(exclude_unset=True).items() 
                       if k in allowed_fields}
    else:
        update_data = task_data.model_dump(exclude_unset=True)
    
    return TaskService.update(db, task_id, update_data)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update task status (workflow transition).
    
    Valid transitions:
    - assigned → in_progress, cancelled
    - in_progress → on_hold, completed, cancelled
    - on_hold → in_progress, cancelled
    - completed → (no transitions)
    - cancelled → (no transitions)
    
    All users can update status on their assigned tasks.
    Admin/Manager can update any task status.
    """
    task = TaskService.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Role-based access check
    if current_user.role == UserRole.EMPLOYEE:
        employee = EmployeeService.get_by_user_id(db, current_user.id)
        if not employee or task.assignee_id != employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return TaskService.update_status(
        db, 
        task_id, 
        status_data.status,
        current_user.id,
        status_data.comment
    )


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Soft delete a task.
    
    **Admin/Manager only**
    """
    TaskService.delete(db, task_id)
    return {"message": "Task deleted successfully"}
