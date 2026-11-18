from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe
from typing import Annotated
from sqlalchemy import update
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import AwareDatetime, BaseModel, Field, StringConstraints


from auth_session import CurrentUser
from database import get_session
from models import ApiToken

router = APIRouter(prefix="/api-tokens", tags=["api-tokens"])
SessionDep = Annotated[Session, Depends(get_session)]


class CreateApiTokenRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True)] = Field(
        min_length=1, max_length=100
    )
    expires_at: AwareDatetime


class CreatedApiToken(BaseModel):
    id: int
    name: str
    expires_at: datetime
    token: str


@router.post(
    "",
    response_model=CreatedApiToken,
    status_code=status.HTTP_201_CREATED,
)
def create_api_token(
    body: CreateApiTokenRequest,
    user: CurrentUser,
    session: SessionDep,
    response: Response,
):
    if user.role != "org_admin" or user.organization_id is None:
        raise HTTPException(status_code=403, detail="Organization admin access required.")

    now = datetime.now(timezone.utc)
    if body.expires_at <= now:
        raise HTTPException(status_code=422, detail="Expiry date must be in the future.")

    raw_token = token_urlsafe(32)
    api_token = ApiToken(
        organization_id=user.organization_id,
        created_by_user_id=user.id,
        name=body.name,
        token_hash=sha256(raw_token.encode("utf-8")).hexdigest(),
        created_at=now,
        expires_at=body.expires_at,
    )
    session.add(api_token)
    session.commit()
    session.refresh(api_token)

    response.headers["Cache-Control"] = "no-store"
    return CreatedApiToken(
        id=api_token.id,
        name=api_token.name,
        expires_at=api_token.expires_at,
        token=raw_token,
    )
@router.get("")
def list_api_tokens(user: CurrentUser, session: SessionDep):
    if user.role != "org_admin" or user.organization_id is None:
        raise HTTPException(status_code=403, detail="Organization admin access required.")

    now = datetime.now(timezone.utc)
    tokens = session.exec(
        select(ApiToken)
        .where(ApiToken.organization_id == user.organization_id)
        .order_by(ApiToken.created_at.desc())
    ).all()

    result = []
    for token in tokens:
        if token.revoked_at is not None:
            token_status = "revoked"
        elif token.expires_at <= now:
            token_status = "expired"
        else:
            token_status = "active"

        result.append({
            "id": token.id,
            "name": token.name,
            "created_by_user_id": token.created_by_user_id,
            "created_at": token.created_at,
            "expires_at": token.expires_at,
            "last_used_at": token.last_used_at or "Never",
            "status": token_status,
        })

    return result


@router.post("/{token_id}/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_token(token_id: int, user: CurrentUser, session: SessionDep):
    if user.role != "org_admin" or user.organization_id is None:
        raise HTTPException(status_code=403, detail="Organization admin access required.")

    now = datetime.now(timezone.utc)
    statement = (
        update(ApiToken)
        .where(
            ApiToken.id == token_id,
            ApiToken.organization_id == user.organization_id,
            ApiToken.revoked_at.is_(None),
            ApiToken.expires_at > now,
        )
        .values(revoked_at=now)
        .returning(ApiToken.id)
    )
    revoked_id = session.execute(statement).scalar_one_or_none()

    if revoked_id is None:
        raise HTTPException(status_code=404, detail="Active token not found.")

    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)