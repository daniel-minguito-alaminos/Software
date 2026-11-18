from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(email: str) -> str:
    return email.strip().lower()


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    __table_args__ = (
        UniqueConstraint("organization_number", name="uq_organizations_number"),
    )

    id: int | None = Field(default=None, primary_key=True)
    organization_number: str = Field(max_length=64)
    created_at: datetime = Field(
        default_factory=_utc_now, sa_type=DateTime(timezone=True)
    )


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("supabase_user_id", name="uq_users_supabase_user_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int | None = Field(
        default=None, foreign_key="organizations.id", ondelete="RESTRICT", index=True
    )
    supabase_user_id: UUID | None = Field(default=None)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: str = Field(max_length=320, unique=True, index=True)
    password_hash: str | None = Field(default=None, max_length=255)
    is_verified: bool = Field(default=False)
    role: str = Field(default="request_user", max_length=32)
    created_at: datetime = Field(
        default_factory=_utc_now, sa_type=DateTime(timezone=True)
    )

class ApiToken(SQLModel, table=True):
    __tablename__ = "api_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_api_tokens_token_hash"),
    )

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    created_by_user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    token_hash: str = Field(max_length=64)
    created_at: datetime = Field(
        default_factory=_utc_now, sa_type=DateTime(timezone=True)
    )
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))
    last_used_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    revoked_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )