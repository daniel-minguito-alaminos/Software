"""Create (or update) a verified test user for local development.

PROVISIONAL (BIZ-32): until registration and email verification exist
(BIZ-24 / BIZ-12), this script is the way to get a user who can log in.

Run from the ``backend`` folder:

    .\\.venv\\Scripts\\python.exe -m scripts.create_test_user tester@example.com

The password is asked for interactively so it never ends up in the shell
history. If the email already exists, its password is replaced and the user
is marked as verified.
"""

import argparse
import getpass
import sys

from sqlmodel import Session, SQLModel, select

from database import engine
from models import User, normalize_email
from passwords import hash_password

MIN_PASSWORD_LENGTH = 8


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a verified test user.")
    parser.add_argument("email", help="Email address of the test user")
    args = parser.parse_args()

    email = normalize_email(args.email)
    if "@" not in email:
        print("Please provide a valid email address.", file=sys.stderr)
        return 1

    password = getpass.getpass("Password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        print(
            f"The password must have at least {MIN_PASSWORD_LENGTH} characters.",
            file=sys.stderr,
        )
        return 1
    if getpass.getpass("Repeat password: ") != password:
        print("The passwords do not match.", file=sys.stderr)
        return 1

    # Only creates the provisional "users" table; other tables are untouched.
    SQLModel.metadata.create_all(engine, tables=[User.__table__])

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user is None:
            user = User(email=email, password_hash="", is_verified=True)
            action = "Created"
        else:
            action = "Updated"
        user.password_hash = hash_password(password)
        user.is_verified = True
        session.add(user)
        session.commit()

    print(f"{action} verified test user {email}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
