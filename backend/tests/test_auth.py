"""Tests for login, logout and protected endpoints (BIZ-32)."""

from datetime import datetime, timedelta, timezone

import jwt

from auth_session import JWT_ALGORITHM, JWT_SECRET_KEY, SESSION_COOKIE_NAME
from conftest import TEST_PASSWORD


def login(client, email, password=TEST_PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def make_token(sub, *, expires_in=timedelta(minutes=5), key=JWT_SECRET_KEY):
    now = datetime.now(timezone.utc)
    payload = {"sub": str(sub), "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, key, algorithm=JWT_ALGORITHM)


# --- Login -----------------------------------------------------------------


def test_verified_user_can_log_in(client, verified_user):
    response = login(client, verified_user.email)

    assert response.status_code == 200
    assert response.json() == {"id": verified_user.id, "email": verified_user.email}
    set_cookie = response.headers["set-cookie"].lower()
    assert set_cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "path=/" in set_cookie


def test_login_email_is_case_and_space_insensitive(client, verified_user):
    response = login(client, "  Verified@Example.COM ")

    assert response.status_code == 200


def test_wrong_password_is_rejected_with_clear_message(client, verified_user):
    response = login(client, verified_user.email, "wrong-password")

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."
    assert SESSION_COOKIE_NAME not in response.cookies


def test_unknown_email_gets_same_message_as_wrong_password(client):
    response = login(client, "nobody@example.com")

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."


def test_unverified_user_cannot_log_in(client, unverified_user):
    response = login(client, unverified_user.email)

    assert response.status_code == 403
    assert "verify your email" in response.json()["detail"]
    assert SESSION_COOKIE_NAME not in response.cookies


def test_unverified_status_not_revealed_with_wrong_password(client, unverified_user):
    response = login(client, unverified_user.email, "wrong-password")

    assert response.status_code == 401


def test_login_with_missing_fields_is_rejected(client):
    assert client.post("/auth/login", json={"email": "a@b.c"}).status_code == 422
    assert client.post("/auth/login", json={"email": "", "password": ""}).status_code == 422


# --- Protected endpoint ----------------------------------------------------


def test_protected_endpoint_works_after_login(client, verified_user):
    login(client, verified_user.email)

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == verified_user.email


def test_protected_endpoint_rejects_missing_cookie(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_protected_endpoint_rejects_garbage_token(client):
    client.cookies.set(SESSION_COOKIE_NAME, "not-a-jwt")

    assert client.get("/auth/me").status_code == 401


def test_protected_endpoint_rejects_token_with_wrong_signature(client, verified_user):
    client.cookies.set(
        SESSION_COOKIE_NAME,
        make_token(verified_user.id, key="another-secret-key-of-at-least-32-chars"),
    )

    assert client.get("/auth/me").status_code == 401


def test_protected_endpoint_rejects_expired_token(client, verified_user):
    client.cookies.set(
        SESSION_COOKIE_NAME,
        make_token(verified_user.id, expires_in=timedelta(minutes=-1)),
    )

    assert client.get("/auth/me").status_code == 401


def test_protected_endpoint_rejects_token_of_deleted_user(client, session, verified_user):
    client.cookies.set(SESSION_COOKIE_NAME, make_token(verified_user.id))
    session.delete(verified_user)
    session.commit()

    assert client.get("/auth/me").status_code == 401


def test_protected_endpoint_rejects_user_no_longer_verified(client, session, verified_user):
    login(client, verified_user.email)
    verified_user.is_verified = False
    session.add(verified_user)
    session.commit()

    assert client.get("/auth/me").status_code == 401


# --- Logout ----------------------------------------------------------------


def test_logout_ends_session(client, verified_user):
    login(client, verified_user.email)
    assert client.get("/auth/me").status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 204
    set_cookie = response.headers["set-cookie"].lower()
    assert set_cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "max-age=0" in set_cookie
    assert client.get("/auth/me").status_code == 401


def test_logout_without_session_is_harmless(client):
    assert client.post("/auth/logout").status_code == 204
