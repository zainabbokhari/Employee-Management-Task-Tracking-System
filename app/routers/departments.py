"""
Department Router - CRUD endpoints for departments
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentDetailResponse,
    DepartmentListResponse
)
from app.services.crud import DepartmentService
from app.utils.security import get_current_user, require_admin, require_manager_or_admin
from app.models.user import User
from app.models.employee import Employee

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get("", response_model=DepartmentListResponse)
async def list_departments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all departments with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Search by name or code
    - **is_active**: Filter by active status
    """
    skip = (page - 1) * page_size
    departments, total = DepartmentService.get_all(
        db, skip=skip, limit=page_size, search=search, is_active=is_active
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return DepartmentListResponse(
        departments=departments,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{department_id}", response_model=DepartmentDetailResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get department details by ID.
    
    Includes employee count and manager name.
    """
    department = DepartmentService.get_by_id(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Get employee count
    employee_count = db.query(Employee).filter(
        Employee.department_id == department_id,
        Employee.is_deleted == False
    ).count()
    
    # Get manager name
    manager_name = None
    if department.manager_id:
        manager = db.query(Employee).filter(Employee.id == department.manager_id).first()
        if manager:
            manager_name = f"{manager.first_name} {manager.last_name}"
    
    return DepartmentDetailResponse(
        **department.__dict__,
        employee_count=employee_count,
        manager_name=manager_name
    )


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new department.
    
    **Admin only**
    
    - **name**: Department name (unique)
    - **code**: Department code (unique)
    - **description**: Optional description
    - **manager_id**: Optional manager employee ID
    """
    return DepartmentService.create(
        db, 
        department_data.model_dump(exclude_unset=True),
        created_by=current_user.id
    )


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update department information.
    
    **Admin only**
    """
    return DepartmentService.update(
        db, 
        department_id, 
        department_data.model_dump(exclude_unset=True)
    )


@router.delete("/{department_id}", status_code=status.HTTP_200_OK)
async def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Soft delete a department.
    
    **Admin only**
    
    Note: Cannot delete department with active employees.
    """
    DepartmentService.delete(db, department_id)
    return {"message": "Department deleted successfully"}
