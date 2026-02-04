"""
Employee Model - Employee records with personal and professional details
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Employee(Base):
    """
    Employee table with detailed information.
    Linked to User for authentication.
    """
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_code = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    
    # Professional Information
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    designation = Column(String(100), nullable=True)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(12, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="employee", foreign_keys=[user_id])
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    project_assignments = relationship("ProjectAssignment", back_populates="employee")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee(id={self.id}, code={self.employee_code}, name={self.full_name})>"


class ProjectAssignment(Base):
    """
    Many-to-many relationship between Employees and Projects
    """
    __tablename__ = "project_assignments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(100), nullable=True)  # Role in project
    assigned_date = Column(Date, server_default=func.current_date())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="project_assignments")
    project = relationship("Project", back_populates="team_members")
