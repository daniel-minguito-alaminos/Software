from datetime import datetime, timezone
from hashlib import sha256
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import update
from sqlmodel import Session

from database import get_session
from models import ApiToken

bearer = HTTPBearer(auto_error=False)


def get_api_token_organization(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_session)],
) -> int:
    unauthorized = HTTPException(
        status_code=401,
        detail="A valid API token is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    now = datetime.now(timezone.utc)
    token_hash = sha256(credentials.credentials.encode("utf-8")).hexdigest()

    statement = (
        update(ApiToken)
        .where(
            ApiToken.token_hash == token_hash,
            ApiToken.revoked_at.is_(None),
            ApiToken.expires_at > now,
        )
        .values(last_used_at=now)
        .returning(ApiToken.organization_id)
    )
    organization_id = session.execute(statement).scalar_one_or_none()

    if organization_id is None:
        raise unauthorized

    session.commit()
    return organization_id


ApiTokenOrganization = Annotated[int, Depends(get_api_token_organization)]