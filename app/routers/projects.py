"""
Project Router - CRUD endpoints for projects
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListResponse
)
from app.models.project import ProjectStatus
from app.services.crud import ProjectService
from app.utils.security import get_current_user, require_admin, require_manager_or_admin
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee, ProjectAssignment
from app.models.task import Task

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    status_filter: Optional[ProjectStatus] = Query(None, alias="status", description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all projects with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Search by name or code
    - **department_id**: Filter by department
    - **status**: Filter by project status
    - **is_active**: Filter by active status
    """
    skip = (page - 1) * page_size
    projects, total = ProjectService.get_all(
        db, 
        skip=skip, 
        limit=page_size, 
        search=search, 
        department_id=department_id,
        status_filter=status_filter,
        is_active=is_active
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project details by ID.
    
    Includes department name, manager name, task count, and team size.
    """
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get department name
    department_name = None
    if project.department_id:
        department = db.query(Department).filter(Department.id == project.department_id).first()
        if department:
            department_name = department.name
    
    # Get manager name
    manager_name = None
    if project.manager_id:
        manager = db.query(Employee).filter(Employee.id == project.manager_id).first()
        if manager:
            manager_name = f"{manager.first_name} {manager.last_name}"
    
    # Get task counts
    task_count = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    ).count()
    
    from app.models.task import TaskStatus
    completed_tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.status == TaskStatus.COMPLETED,
        Task.is_deleted == False
    ).count()
    
    # Get team size
    team_size = db.query(ProjectAssignment).filter(
        ProjectAssignment.project_id == project_id,
        ProjectAssignment.is_active == True
    ).count()
    
    return ProjectDetailResponse(
        **project.__dict__,
        department_name=department_name,
        manager_name=manager_name,
        task_count=task_count,
        completed_tasks=completed_tasks,
        team_size=team_size
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Create a new project.
    
    **Admin/Manager only**
    
    - **name**: Project name
    - **code**: Project code (unique)
    - **department_id**: Associated department
    - **manager_id**: Project manager (employee ID)
    - **status**: Project status (default: planning)
    - **priority**: Project priority (default: medium)
    """
    return ProjectService.create(
        db, 
        project_data.model_dump(exclude_unset=True),
        created_by=current_user.id
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Update project information.
    
    **Admin/Manager only**
    """
    return ProjectService.update(
        db, 
        project_id, 
        project_data.model_dump(exclude_unset=True)
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Soft delete a project.
    
    **Admin only**
    """
    ProjectService.delete(db, project_id)
    return None
