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
        "client_secret": settings.management_client_secret.get_secret_value(),
        "audience": settings.auth_audience,
    }
    response = requests.post(
        f"https://{settings.auth_domain}/oauth/token", json=payload, headers=headers
    )
    data = response.json()
    return data["access_token"]


def main() -> None:
    """Generate an Auth0 access token."""
    import typer
    typer.echo(get_access_token())


if __name__ == "__main__":
    import typer
    typer.run(main)
