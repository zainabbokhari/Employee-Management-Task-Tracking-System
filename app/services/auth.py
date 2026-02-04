"""
Authentication Service - Business logic for user authentication
"""
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, LoginRequest, LoginResponse, UserResponse
from app.utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token
)
from app.config import settings
from app.utils.logger import logger


class AuthService:
    """Authentication service class"""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.EMPLOYEE
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created: {db_user.email}")
        return db_user
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> LoginResponse:
        """Login user and return token"""
        user = AuthService.authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),  # Convert to string as per JWT standard
                "email": user.email,
                "role": user.role.value
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
