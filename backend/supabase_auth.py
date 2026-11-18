import os
from uuid import UUID

import httpx
from fastapi import HTTPException


def _provider_json(
    response: httpx.Response,
    rejected_statuses: set[int],
    rejection_message: str,
) -> dict:
    if response.status_code in rejected_statuses:
        raise HTTPException(status_code=401, detail=rejection_message)

    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Try again later.",
        )

    if not response.is_success:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable.",
        )

    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Unexpected response from Supabase Auth")

    return data


def authenticate_supabase_user(email: str, password: str) -> UUID:
    base_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    public_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not base_url or not public_key:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable.",
        )

    try:
        with httpx.Client(
            base_url=f"{base_url}/auth/v1/",
            headers={"apikey": public_key},
            timeout=8.0,
        ) as client:
            login_response = client.post(
                "token",
                params={"grant_type": "password"},
                json={"email": email, "password": password},
            )
            login_data = _provider_json(
                login_response,
                {400, 401, 403, 422},
                "Incorrect email or password.",
            )

            token = login_data.get("access_token")
            if not isinstance(token, str) or not token:
                raise ValueError("Missing access token")

            user_response = client.get(
                "user",
                headers={"Authorization": f"Bearer {token}"},
            )
            identity = _provider_json(
                user_response,
                {401, 403},
                "Authentication could not be verified.",
            )

            if not identity.get("email_confirmed_at"):
                raise HTTPException(
                    status_code=403,
                    detail="Please verify your email.",
                )

            return UUID(identity["id"])

    except (httpx.HTTPError, TypeError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable.",
        ) from exc

def send_registration_invite(email: str) -> UUID:
    base_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

    if not base_url or not secret_key or not frontend_url:
        raise HTTPException(
            status_code=503, detail="Email invitations are not configured."
        )

    try:
        response = httpx.post(
            f"{base_url}/auth/v1/invite",
            headers={"apikey": secret_key},
            params={"redirect_to": f"{frontend_url}/set-password"},
            json={"email": email},
            timeout=10.0,
        )

        if response.status_code == 429:
            raise HTTPException(
                status_code=429, detail="Please wait before trying again."
            )

        response.raise_for_status()
        return UUID(response.json()["id"])

    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=503, detail="The invitation could not be sent."
        ) from exc