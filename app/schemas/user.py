"""
User Schemas - Pydantic models for User API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# Base Schema
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: Optional[UserRole] = UserRole.EMPLOYEE


# Create Schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


# Update Schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# Password Update
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


# Response Schema
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


# Login Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Response with user info
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
