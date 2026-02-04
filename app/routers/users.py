from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.utils.security import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new user. Only ADMIN can create users."""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create users")

    return AuthService.create_user(db, user_data)
