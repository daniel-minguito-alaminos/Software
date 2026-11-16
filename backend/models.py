"""Database models.

PROVISIONAL (BIZ-32): this minimal ``User`` model only exists so that login
and logout can be implemented and demonstrated. The final user and
organization schema is defined in BIZ-34, which will replace or extend this
model (and the ``users`` table).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(email: str) -> str:
    """Emails are stored and compared in lowercase without surrounding spaces."""
    return email.strip().lower()


class User(SQLModel, table=True):
    # PROVISIONAL (BIZ-32): BIZ-34 replaces/extends this model.
    __tablename__ = "users"  # "user" is a reserved word in PostgreSQL

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=320, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=_utc_now,
        sa_type=DateTime(timezone=True),
    )
