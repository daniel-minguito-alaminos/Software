"""Test setup: in-memory SQLite database, never the shared PostgreSQL database."""

import os

# Must run before the app is imported. Assigning (not setdefault) guarantees
# that values from backend/.env are never used: load_dotenv does not override
# variables that already exist. The dummy PostgreSQL URL is never connected to
# because get_session is overridden below.
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:1/not-used-in-tests"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-at-least-32-characters"
os.environ["JWT_EXPIRE_MINUTES"] = "60"
os.environ["SESSION_COOKIE_SECURE"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from database import get_session  # noqa: E402
from main import app  # noqa: E402
from models import User  # noqa: E402
from passwords import hash_password  # noqa: E402

TEST_PASSWORD = "correct-horse-battery"


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _add_user(session, email, verified):
    user = User(email=email, password_hash=hash_password(TEST_PASSWORD), is_verified=verified)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def verified_user(session):
    return _add_user(session, "verified@example.com", verified=True)


@pytest.fixture
def unverified_user(session):
    return _add_user(session, "unverified@example.com", verified=False)
