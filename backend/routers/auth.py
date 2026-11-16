"""Login, logout and current-user endpoints (BIZ-32)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from auth_session import CurrentUser, clear_session_cookie, set_session_cookie
from database import get_session
from models import User, normalize_email
from passwords import DUMMY_PASSWORD_HASH, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

SessionDep = Annotated[Session, Depends(get_session)]

INVALID_CREDENTIALS = "Incorrect email or password."
NOT_VERIFIED = "Please verify your email address before logging in."


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class UserRead(BaseModel):
    id: int
    email: str


@router.post("/login", response_model=UserRead)
def login(credentials: LoginRequest, response: Response, session: SessionDep):
    email = normalize_email(credentials.email)
    user = session.exec(select(User).where(User.email == email)).first()

    if user is None:
        # Same work as a real check, so response time does not reveal
        # whether the email is registered.
        verify_password(credentials.password, DUMMY_PASSWORD_HASH)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, INVALID_CREDENTIALS)

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, INVALID_CREDENTIALS)

    # Only reported once the password is correct.
    if not user.is_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, NOT_VERIFIED)

    set_session_cookie(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    clear_session_cookie(response)


@router.get("/me", response_model=UserRead)
def read_current_user(user: CurrentUser):
    """Example protected endpoint: returns the logged-in user."""
    return user
