"""Functions to verify auth tokens."""
from typing import Any, Dict

import jwt

from app.core.config import get_settings


class VerifyToken:
    """Verify Auth0 token.

    Does all the token verification using `PyJWT <https://pyjwt.readthedocs.io/en/stable/>`__.
    """

    def _set_up(self):
        settings = get_settings()
        config = {
            "DOMAIN": settings.auth_domain,
            # Note that we have two audiences her,
            "API_AUDIENCE": [settings.auth_client_id, settings.auth_audience],
            "ISSUER": f"https://{settings.auth_domain}/",
            "ALGORITHMS": settings.auth_algorithms,
        }
        return config

    def __init__(self, token, permissions=None, scopes=None) -> None:
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.config = self._set_up()

        # This gets the JWKS from a given URL and does processing so you can use any of
        # the keys available
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=[self.config["ALGORITHMS"]],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if self.scopes:
            result = self._check_claims(payload, "scope", str, self.scopes.split(" "))
            if result.get("error"):
                return result

        if self.permissions:
            result = self._check_claims(payload, "permissions", list, self.permissions)
            if result.get("error"):
                return result

        return payload

    def _check_claims(
        self, payload, claim_name, claim_type, expected_value
    ) -> Dict[str, Any]:

        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result

        if claim_name == "scope":
            payload_claim = payload[claim_name].split(" ")

        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403

                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (
                    f"Insufficient {claim_name} ({value}). You don't have "
                    "access to this resource"
                )
                return result
        return result