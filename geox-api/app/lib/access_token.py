from . import config

import requests

payload = {
    "grant_type": "client_credentials",
    "client_id": config.management_client_id,
    "client_secret": config.management_client_secret,
    "audience": config.auth_audience,
}

headers = {"content-type": "application/json"}


def get_access_token() -> str:
    """Get access token from Auth0

    See https://auth0.com/docs/secure/tokens/access-tokens/get-management-api-access-tokens-for-production
    """
    response = requests.post(
        f"https://{config.auth_domain}/oauth/token", json=payload, headers=headers
    )
    data = response.json()
    return data["access_token"]
