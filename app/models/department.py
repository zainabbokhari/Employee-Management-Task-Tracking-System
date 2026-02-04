"""
Department Model - Organizational units
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Department(Base):
    """
    Department table for organizing employees.
    """
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)
    projects = relationship("Project", back_populates="department")
    
    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name})>"
