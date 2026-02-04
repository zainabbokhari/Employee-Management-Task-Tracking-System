"""
Task Schemas - Pydantic models for Task API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.task import TaskStatus, TaskPriority


# Base Schema
class TaskBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None


# Create Schema
class TaskCreate(TaskBase):
    pass


# Update Schema
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


# Status Update (for workflow)
class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    comment: Optional[str] = None


# Response Schema
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    completed_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# Detailed Response
class TaskDetailResponse(TaskResponse):
    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    created_by_name: Optional[str] = None


# List Response with pagination
class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Task Comment
class TaskCommentCreate(BaseModel):
    comment: str = Field(..., min_length=1)


class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Task Statistics
class TaskStats(BaseModel):
    total: int
    assigned: int
    in_progress: int
    completed: int
    overdue: int
