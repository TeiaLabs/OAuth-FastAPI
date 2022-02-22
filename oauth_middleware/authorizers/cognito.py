import time
from binascii import Error
from typing import Callable
from typing import Tuple

import requests
from jose import jwk
from jose import jwt
from jose.exceptions import JWKError
from jose.utils import base64url_decode
from requests.exceptions import BaseHTTPError

from .authorizer import Authorizer
from ..utils import timed_cache


class CognitoAuthorizer(Authorizer):
    def __init__(
            self,
            region: str,
            user_pool: str,
            app_client_id: str,
            token_type: str,
            token_validator: Callable = lambda _: (True, "")
    ):
        self.issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool}"
        self.jwk_address = f"{self.issuer}/.well-known/jwks.json"
        self.user_pool_id = user_pool
        self.app_client_id = app_client_id
        self.token_type = token_type
        self.token_validator = token_validator

    def validate_token(self, token: str) -> Tuple[bool, str]:
        is_valid, resp = self.verify_signing_key(token)
        if not is_valid:
            return False, resp

        is_valid, resp = self.verify_claims(token)
        if not is_valid:
            return False, resp

        return self.token_validator(token)

    def verify_signing_key(self, token):
        try:
            message, encoded_signature = str(token).rsplit(".", 1)

            key = self.get_signing_key(token)
            if key is None:
                return False, "Token is not valid"

            public_key = jwk.construct(key)
            decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

            if not public_key.verify(message.encode("utf8"), decoded_signature):
                return False, "Token is not valid"

            return True, ""

        except BaseHTTPError:
            return False, "Failed to recover server keys"
        except JWKError:
            return False, "Server key is not valid"
        except (Error, ValueError, IndexError):
            return False, "Token is not valid"

    def verify_claims(self, token):
        claims = jwt.get_unverified_claims(token)
        if time.time() > claims["exp"]:
            return False, "Token is expired"

        if claims["iss"] != self.issuer:
            return False, "Token is not valid"

        if self.token_type and self.token_type != claims["token_use"]:
            return False, "Token is not valid"

        if self.app_client_id and claims["client_id"] != self.app_client_id:
            return False, "Token is not valid"

        for group in claims["cognito:groups"]:
            if group.startswith(self.user_pool_id):
                return True, ""

        return False, "Token is not valid"

    def get_signing_key(self, token):
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]

        keys = self._get_keys()
        for key in keys["keys"]:
            if key["kid"] == kid:
                return key

        return None

    @timed_cache(3600)
    def _get_keys(self):
        return requests.get(self.jwk_address).json()
