"""
Employee Schemas - Pydantic models for Employee API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Base Schema
class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = Field(None, max_length=100)
    hire_date: date
    salary: Optional[Decimal] = Field(None, ge=0)


# Create Schema
class EmployeeCreate(EmployeeBase):
    employee_code: Optional[str] = None  # Auto-generated if not provided
    create_user_account: bool = False
    password: Optional[str] = Field(None, min_length=6)


# Update Schema
class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    salary: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


# Response Schema
class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    hire_date: date
    salary: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Detailed Response with department info
class EmployeeDetailResponse(EmployeeResponse):
    department_name: Optional[str] = None
    full_name: str
    task_count: Optional[int] = 0
    user_id: Optional[int] = None


# List Response with pagination
class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Simple employee reference
class EmployeeSimple(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    
    class Config:
        from_attributes = True
