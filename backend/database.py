import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlmodel import Session, create_engine

load_dotenv(Path(__file__).with_name(".env"))

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("Set DATABASE_URL in backend/.env")

url = make_url(database_url).set(drivername="postgresql+psycopg")
engine = create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 10})


def get_session():
    """FastAPI dependency that yields a database session per request.

    Tests override this dependency to use an in-memory SQLite database.
    """
    with Session(engine) as session:
        yield session
