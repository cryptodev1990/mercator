
"""Functions to generate an auth tokens."""
import requests
from app.core.config import get_settings


def get_access_token() -> str:
    """Get access token from Auth0.

    See https://auth0.com/docs/secure/tokens/access-tokens/get-management-api-access-tokens-for-production
    """
    settings = get_settings()
    headers = {"content-type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.management_client_id,
        "client_secret": settings.management_client_secret,
        "audience": settings.auth_audience,
    }
    print(payload)
    response = requests.post(
        f"https://{settings.auth_domain}/oauth/token", json=payload, headers=headers
    )
    data = response.json()
    return data["access_token"]
