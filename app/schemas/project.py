"""
Project Schemas - Pydantic models for Project API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.project import ProjectStatus, ProjectPriority


# Base Schema
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[ProjectStatus] = ProjectStatus.PLANNING
    priority: Optional[ProjectPriority] = ProjectPriority.MEDIUM
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[int] = None


# Create Schema
class ProjectCreate(ProjectBase):
    pass


# Update Schema
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Optional[int] = None
    is_active: Optional[bool] = None


# Response Schema
class ProjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: ProjectStatus
    priority: ProjectPriority
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Detailed Response
class ProjectDetailResponse(ProjectResponse):
    department_name: Optional[str] = None
    manager_name: Optional[str] = None
    task_count: Optional[int] = 0
    completed_tasks: Optional[int] = 0
    team_size: Optional[int] = 0


# List Response with pagination
class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Team member assignment
class ProjectTeamMember(BaseModel):
    employee_id: int
    role: Optional[str] = None


class ProjectTeamUpdate(BaseModel):
    members: List[ProjectTeamMember]
