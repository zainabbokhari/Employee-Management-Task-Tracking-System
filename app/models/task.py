"""
Task Model - Task tracking with workflow
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TaskStatus(str, enum.Enum):
    """Task workflow statuses"""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """
    Task table with workflow management.
    Tasks can be assigned to employees and linked to projects.
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Task details
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.ASSIGNED, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Timeline
    due_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    
    # Estimation
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    
    # Progress (0-100)
    progress = Column(Integer, default=0)
    
    # Status flags
    is_deleted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("Employee", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    created_by_user = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class TaskComment(Base):
    """
    Comments on tasks for collaboration
    """
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User")
