"""Login, logout and current-user endpoints (BIZ-32)."""

from typing import Annotated

from supabase_auth import authenticate_supabase_user, send_registration_invite
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from auth_session import CurrentUser, clear_session_cookie, set_session_cookie
from database import get_session
from models import Organization, User, normalize_email
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
    if user is not None and user.supabase_user_id is not None:
        supabase_id = authenticate_supabase_user(email, credentials.password)

        if supabase_id != user.supabase_user_id:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                INVALID_CREDENTIALS,
            )

        if not user.is_verified:
            if user.organization_id is None or user.password_hash is not None:
                raise HTTPException(status.HTTP_403_FORBIDDEN, NOT_VERIFIED)

            user.is_verified = True
            session.add(user)
            session.commit()
            session.refresh(user)

        set_session_cookie(response, user)
        return user

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

class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    organization_number: str = Field(min_length=1, max_length=64)


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
def register_organization(body: RegisterRequest, session: SessionDep):
    email = normalize_email(str(body.email))

    try:
        with session.begin():
            organization = Organization(
                organization_number=body.organization_number.upper(),
            )
            session.add(organization)
            session.flush()

            user = User(
              email=email,
              first_name=body.first_name,
              last_name=body.last_name,
              organization_id=organization.id,
              role="org_admin",
              is_verified=False,
            )
            session.add(user)
            session.flush()

            user.supabase_user_id = send_registration_invite(email)

    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account or organization already exists with these details.",
        ) from exc

    return {"message": "Check your inbox for your verification link."}