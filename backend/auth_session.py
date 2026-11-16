"""Application session handling: JWT stored in an HttpOnly cookie.

All session logic lives in this module so it can be replaced in one place if
the authentication framework (BIZ-31) chooses a different mechanism.

The rest of the backend only uses:
- ``set_session_cookie(response, user)`` after a successful login,
- ``clear_session_cookie(response)`` on logout,
- ``CurrentUser`` (or ``Depends(get_current_user)``) to protect endpoints.

Note: the JWT is stateless, so logout removes the cookie from the browser but
a copied token stays valid until it expires. Keep JWT_EXPIRE_MINUTES short; a
server-side denylist can be added in BIZ-31 if needed.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from sqlmodel import Session

from database import get_session  # also loads backend/.env
from models import User

SESSION_COOKIE_NAME = "bpc_session"
JWT_ALGORITHM = "HS256"
MIN_SECRET_KEY_LENGTH = 32

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if len(JWT_SECRET_KEY) < MIN_SECRET_KEY_LENGTH:
    raise RuntimeError(
        f"Set JWT_SECRET_KEY in backend/.env (at least {MIN_SECRET_KEY_LENGTH} characters)"
    )

JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
# Must be "true" in production (HTTPS). Local development runs on plain HTTP.
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Return the user id stored in a valid token, or None if it is invalid/expired."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None


def _cookie_options() -> dict:
    return {
        "httponly": True,
        "secure": SESSION_COOKIE_SECURE,
        "samesite": "lax",
        "path": "/",
    }


def set_session_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        create_access_token(user.id),
        max_age=JWT_EXPIRE_MINUTES * 60,
        **_cookie_options(),
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, **_cookie_options())


def get_current_user(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Dependency for protected endpoints: returns the logged-in user or raises 401."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )

    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise unauthorized

    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized

    user = session.get(User, user_id)
    if user is None or not user.is_verified:
        raise unauthorized

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
