from sqlalchemy import text

from database import engine

with engine.connect() as connection:
    name = connection.execute(text("SELECT current_database()")).scalar_one()
    print(f"Connected to PostgreSQL: {name}")