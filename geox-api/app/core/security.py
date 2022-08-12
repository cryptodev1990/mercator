from typing import Any, Dict, List, Optional, Type, Union

import jwt
from fastapi.security import HTTPBearer

from app.core.config import Settings

token_auth_scheme = HTTPBearer()


class VerifyToken:
    """Verify Auth0 token.

    Does all the token verification using `PyJWT <https://pyjwt.readthedocs.io/en/stable/>`__.
    """

    def __init__(
        self,
        token: str,
        settings: Settings,
        permissions=None,
        scopes: Optional[str] = None,
    ) -> None:
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        # Settings
        self.domain = settings.auth_domain
        self.api_audience = [settings.auth_client_id, settings.auth_audience]
        self.issuer = f"https://{settings.auth_domain}/"
        self.algorithms = [settings.auth_algorithms]

        # This gets the JWKS from a given URL and does processing so you can use any of
        # the keys available
        jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self) -> Dict[str, Any]:
        """Verify the JWT."""
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
                algorithms=self.algorithms,
                audience=self.api_audience,
                issuer=self.issuer,
            )
        except Exception as e:
            return {"status": "error", "msg": str(e)}

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
        self,
        payload: Dict[str, Any],
        claim_name: str,
        claim_type: Union[Type[str], Type[list]],
        expected_value: List[str],
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
