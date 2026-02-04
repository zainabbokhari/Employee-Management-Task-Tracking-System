"""
Department Schemas - Pydantic models for Department API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Base Schema
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


# Create Schema
class DepartmentCreate(DepartmentBase):
    manager_id: Optional[int] = None


# Update Schema
class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


# Response Schema
class DepartmentResponse(DepartmentBase):
    id: int
    manager_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Detailed Response with employee count
class DepartmentDetailResponse(DepartmentResponse):
    employee_count: Optional[int] = 0
    manager_name: Optional[str] = None


# List Response with pagination
class DepartmentListResponse(BaseModel):
    departments: List[DepartmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
