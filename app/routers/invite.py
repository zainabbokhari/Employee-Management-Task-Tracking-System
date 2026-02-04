from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.utils.security import create_access_token, decode_token
from app.utils.security import require_admin
from app.models.user import UserRole
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.config import settings
from app.utils.mailer import send_email


class InviteCreate(BaseModel):
    email: EmailStr
    role: UserRole


class InviteAccept(BaseModel):
    token: str
    email: EmailStr
    password: str
    full_name: str

router = APIRouter(prefix="/api/invite", tags=["Invites"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_invite(invite: InviteCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Admin creates an invite token for given role+email. In production, send this token via email."""
    data = {"role": invite.role.value, "email": invite.email}
    token = create_access_token(data=data, expires_delta=timedelta(hours=24))

    # Try to send email if SMTP configured
    sent = False
    # Build invite accept link (frontend page)
    path = f"/static/invite_accept.html?token={token}"
    if settings.FRONTEND_URL:
        invite_link = settings.FRONTEND_URL.rstrip('/') + path
    else:
        invite_link = path
    if settings.EMAIL_HOST and settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
        subject = "You're invited to Employee Management System"
        body = f"You have been invited to the system as {invite.role.value}.\n\nUse this link to accept the invite and set your password:\n{invite_link}\n\nThe link expires in 24 hours."
        sent = send_email(to_email=invite.email, subject=subject, body=body)

    return {"invite_token": token, "expires_in_hours": 24, "email_sent": sent, "invite_link": invite_link}


@router.post("/accept", response_model=UserResponse)
def accept_invite(payload: InviteAccept, db: Session = Depends(get_db)):
    """Accept an invite token and create the user. Token must include role."""
    token_data = decode_token(payload.token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    role_str = token_data.role
    if not role_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite token missing role")

    # override the role from token to prevent privilege escalation
    # Create UserCreate from payload and enforce role from token
    user_create = UserCreate(email=payload.email, password=payload.password, full_name=payload.full_name, role=UserRole(role_str))
    return AuthService.create_user(db, user_create)
