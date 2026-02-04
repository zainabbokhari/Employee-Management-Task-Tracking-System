"""
Project Model - Project management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """Project status options"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, enum.Enum):
    """Project priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Project(Base):
    """
    Project table for tracking organizational projects.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Project details
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    priority = Column(SQLEnum(ProjectPriority), default=ProjectPriority.MEDIUM)
    
    # Timeline
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Budget
    budget = Column(Integer, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    department = relationship("Department", back_populates="projects")
    manager = relationship("Employee", foreign_keys=[manager_id])
    tasks = relationship("Task", back_populates="project")
    team_members = relationship("ProjectAssignment", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
