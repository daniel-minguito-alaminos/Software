from alembic import context
from sqlmodel import SQLModel

import models  # Register the application tables in SQLModel.metadata.


def run_migrations() -> None:
    if context.is_offline_mode():
        context.configure(
            dialect_name="postgresql",
            target_metadata=SQLModel.metadata,
            literal_binds=True,
        )
        with context.begin_transaction():
            context.run_migrations()
        return

    from database import engine

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=SQLModel.metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
