"""
Authentication Router - Login, Register, and Token endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    LoginRequest, 
    LoginResponse,
    Token
)
from app.services.auth import AuthService
from app.utils.security import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Minimum 6 characters
    - **full_name**: User's full name
    - **role**: Optional role (default: employee)
    """
    # Gate public registration behind configuration
    if not settings.ALLOW_PUBLIC_REGISTRATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Public registration is disabled")

    return AuthService.create_user(db, user_data)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns JWT access token and user information.
    """
    return AuthService.login(db, login_data)


@router.post("/token", response_model=Token)
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login.
    
    Use this endpoint for OAuth2 password flow.
    """
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    response = AuthService.login(db, login_data)
    return Token(access_token=response.access_token, token_type=response.token_type)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user information.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    Note: For JWT, logout is handled client-side by removing the token.
    This endpoint is provided for logging purposes.
    """
    return {"message": "Successfully logged out"}
