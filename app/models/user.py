"""
User Model - For authentication and authorization
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(Base):
    """
    User table for authentication.
    Separate from Employee to allow flexible user management.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="user", uselist=False, foreign_keys="Employee.user_id")
    created_tasks = relationship("Task", back_populates="created_by_user", foreign_keys="Task.created_by")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
