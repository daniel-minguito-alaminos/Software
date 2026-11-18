
from uuid import UUID
from sqlmodel import select
from models import Organization, User

# TEST 1-successful registration
def test_organization_registration(client, session, monkeypatch):
    #fake email
    def fake_invite(email):
        return UUID("12345678-1234-1234-1234-123456789012")
    monkeypatch.setattr("routers.auth.send_registration_invite", fake_invite)
   #new user
    response = client.post("/auth/register", json={
        "first_name": "Anna",
        "last_name": "Smith",
        "email": "newuser@example.com",
        "organization_number": "AT12345678"
    })
    assert response.status_code == 202
    # checking the organization
    organization = session.exec(select(Organization)).first()
    assert organization is not None
    assert organization.organization_number == "AT12345678"
    # checking the user
    user = session.exec(select(User)).first()
    assert user is not None
    assert user.email == "newuser@example.com"
    # checking the connection
    assert user.organization_id == organization.id
    assert user.is_verified is False
    assert user.role == "org_admin"
    assert user.supabase_user_id is not None

# TEST 2-invalid email
def test_invalid_registration(client):
    response = client.post("/auth/register", json={
        "first_name": "Anna",
        "last_name": "Smith",
        "email": "wrong-email",
        "organization_number": "AT12345678"
    })
    assert response.status_code == 422

# TEST 3-duplicate registration
def test_duplicate_registration(client, monkeypatch):
    def fake_invite(email):
        return UUID("12345678-1234-1234-1234-123456789012")
    monkeypatch.setattr("routers.auth.send_registration_invite", fake_invite)
   #registration data
    data = {
        "first_name": "Anna",
        "last_name": "Smith",
        "email": "duplicate@example.com",
        "organization_number": "AT99999999"
    }
    response1 = client.post("/auth/register", json=data)
    assert response1.status_code == 202
    response2 = client.post("/auth/register", json=data)
    assert response2.status_code == 409

# TEST 4-unverified user cannot log in
def test_unverified_user_cannot_login(client, monkeypatch):
    # fake email invitation
    def fake_invite(email):
        return UUID("12345678-1234-1234-1234-123456789012")
    monkeypatch.setattr("routers.auth.send_registration_invite", fake_invite)
    # registering a new user
    response = client.post("/auth/register", json={
        "first_name": "Anna",
        "last_name": "Smith",
        "email": "unverified-new@example.com",
        "organization_number": "AT55555555"
    })
    assert response.status_code == 202
    # trying to log in before email verification
    login_response = client.post("/auth/login", json={
        "email": "unverified-new@example.com",
        "password": "testpassword123"
    })
    assert login_response.status_code != 200
    # protected page must not be accessible
    protected_response = client.get("/auth/me")
    assert protected_response.status_code == 401


# TEST 5-login, protected page and logout
def test_login_and_logout(client, verified_user):
    # login
    response = client.post("/auth/login", json={
        "email": verified_user.email,
        "password": "correct-horse-battery"
    })
    assert response.status_code == 200
    # access to protected page
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == verified_user.email
    # logout
    response = client.post("/auth/logout")
    assert response.status_code == 204
    # try to access protected page after logout
    response = client.get("/auth/me")
    assert response.status_code == 401


# TEST 6-login after verification
def test_login_after_verification(client, session, monkeypatch):
    # fake user ID
    user_id = UUID("12345678-1234-1234-1234-123456789012")
    # fake email invitation
    def fake_invite(email):
        return user_id
    monkeypatch.setattr("routers.auth.send_registration_invite", fake_invite)
    # register a new user
    response = client.post("/auth/register", json={
        "first_name": "Anna",
        "last_name": "Smith",
        "email": "anna@example.com",
        "organization_number": "AT77777777"
    })
    assert response.status_code == 202
    # user isn't verified yet
    user = session.exec(select(User)).first()
    assert user.is_verified is False
    # fake authentication
    def fake_auth(email, password):
        return user_id
    monkeypatch.setattr("routers.auth.authenticate_supabase_user", fake_auth)
    # login after verification
    response = client.post("/auth/login", json={
        "email": "anna@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    # checking that the user is verified
    session.refresh(user)
    assert user.is_verified is True
    # checking protected page
    response = client.get("/auth/me")
    assert response.status_code == 200
