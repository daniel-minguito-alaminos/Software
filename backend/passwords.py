"""Password hashing with Argon2 (via pwdlib)."""

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()

# Hash of a random value, used to verify against when the user does not exist,
# so a failed login takes the same time whether or not the email is registered.
DUMMY_PASSWORD_HASH = _password_hash.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if password_hash is None:
        _password_hash.verify(password, DUMMY_PASSWORD_HASH)
        return False

    return _password_hash.verify(password, password_hash)
