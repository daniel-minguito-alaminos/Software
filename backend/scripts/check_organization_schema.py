"""Insert and read a linked organization and user, then roll back the check."""

from uuid import uuid4

from sqlmodel import Session, select

from database import engine
from models import Organization, User


def main() -> None:
    identifier = uuid4()
    with Session(engine) as session:
        organization = Organization(organization_number=f"schema-check-{identifier}")
        session.add(organization)
        session.flush()

        user = User(
            email=f"schema-check-{identifier}@example.invalid",
            first_name="Schema",
            last_name="Check",
            organization_id=organization.id,
            supabase_user_id=identifier,
            is_verified=True,
        )
        session.add(user)
        session.flush()
        session.expunge_all()

        statement = (
            select(User, Organization)
            .join(Organization, User.organization_id == Organization.id)
            .where(User.supabase_user_id == identifier)
        )
        saved_user, saved_organization = session.exec(statement).one()
        if saved_user.organization_id != saved_organization.id:
            raise RuntimeError("The retrieved user has an unexpected organization.")

        session.rollback()

    print("OK: organization and linked user saved and retrieved; changes rolled back.")


if __name__ == "__main__":
    main()
