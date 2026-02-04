"""
Employee Router - CRUD endpoints for employees
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeDetailResponse,
    EmployeeListResponse,
    EmployeeSimple
)
from app.services.crud import EmployeeService
from app.services.auth import AuthService
from app.utils.security import get_current_user, require_admin, require_manager_or_admin
from app.models.user import User, UserRole
from app.models.department import Department
from app.schemas.user import UserCreate

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email, or code"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all employees with pagination and filtering.
    
    - **Admin/Manager**: Can see all employees
    - **Employee**: Can only see their own profile
    """
    # Role-based filtering
    if current_user.role == UserRole.EMPLOYEE:
        # Employees can only see their own profile
        employee = EmployeeService.get_by_user_id(db, current_user.id)
        if employee:
            return EmployeeListResponse(
                employees=[employee],
                total=1,
                page=1,
                page_size=1,
                total_pages=1
            )
        return EmployeeListResponse(
            employees=[],
            total=0,
            page=1,
            page_size=1,
            total_pages=0
        )
    
    skip = (page - 1) * page_size
    employees, total = EmployeeService.get_all(
        db, 
        skip=skip, 
        limit=page_size, 
        search=search, 
        department_id=department_id,
        is_active=is_active
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return EmployeeListResponse(
        employees=employees,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/simple", response_model=list[EmployeeSimple])
async def list_employees_simple(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get simple list of all active employees (for dropdowns).
    """
    employees, _ = EmployeeService.get_all(db, limit=1000, is_active=True)
    return [
        EmployeeSimple(
            id=e.id,
            employee_code=e.employee_code,
            full_name=f"{e.first_name} {e.last_name}",
            email=e.email
        )
        for e in employees
    ]


@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get employee details by ID.
    
    - **Admin/Manager**: Can see any employee
    - **Employee**: Can only see their own profile
    """
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Role-based access check
    if current_user.role == UserRole.EMPLOYEE:
        user_employee = EmployeeService.get_by_user_id(db, current_user.id)
        if not user_employee or user_employee.id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Get department name
    department_name = None
    if employee.department_id:
        department = db.query(Department).filter(Department.id == employee.department_id).first()
        if department:
            department_name = department.name
    
    # Get task count
    from app.models.task import Task
    task_count = db.query(Task).filter(
        Task.assignee_id == employee_id,
        Task.is_deleted == False
    ).count()
    
    return EmployeeDetailResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        date_of_birth=employee.date_of_birth,
        address=employee.address,
        department_id=employee.department_id,
        designation=employee.designation,
        hire_date=employee.hire_date,
        salary=employee.salary,
        is_active=employee.is_active,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
        full_name=f"{employee.first_name} {employee.last_name}",
        department_name=department_name,
        task_count=task_count,
        user_id=employee.user_id
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new employee.
    
    **Admin only**
    
    - **employee_code**: Auto-generated if not provided
    - **create_user_account**: If true, creates a user account for login
    - **password**: Required if create_user_account is true
    """
    data = employee_data.model_dump(exclude={"create_user_account", "password"})
    
    # Create user account if requested
    if employee_data.create_user_account:
        if not employee_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password required when creating user account"
            )
        
        user_data = UserCreate(
            email=employee_data.email,
            password=employee_data.password,
            full_name=f"{employee_data.first_name} {employee_data.last_name}",
            role=UserRole.EMPLOYEE
        )
        user = AuthService.create_user(db, user_data)
        data["user_id"] = user.id
    
    return EmployeeService.create(db, data, created_by=current_user.id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update employee information.
    
    **Admin only**
    """
    return EmployeeService.update(
        db, 
        employee_id, 
        employee_data.model_dump(exclude_unset=True)
    )


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Soft delete an employee.
    
    **Admin only**
    """
    EmployeeService.delete(db, employee_id)
    return {"message": "Employee deleted successfully"}
