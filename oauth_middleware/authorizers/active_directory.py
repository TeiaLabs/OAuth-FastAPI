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
from ..utils.cache import timed_cache


def get_alg_key(kty):
    if kty == "RSA":
        return "RS256"


class ADAuthorizer(Authorizer):
    def __init__(
            self,
            tenant: str,
            app_client_id: str = "",
            token_validator: Callable = lambda _: (True, "")
    ):
        self.app_client_id = app_client_id
        self.token_validator = token_validator
        self.address = f"https://login.microsoftonline.com/{tenant}/discovery/keys"

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
            key = self.get_signing_key(token)
            if key is None:
                return False, "Token is not valid"

            public_key = jwk.construct(key)
            message, encoded_signature = str(token).rsplit('.', 1)
            decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

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
        if time.time() > claims['exp']:
            return False, "Token is expired"

        if claims['aud'] != self.app_client_id:
            return False, "Token is not valid"

        return self.token_validator(token)

    def get_signing_key(self, token):
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]

        keys = self._get_keys()
        for key in keys["keys"]:
            if key['kid'] == kid:
                key["alg"] = get_alg_key(key["kty"])
                return key

        return None

    @timed_cache(3600)
    def _get_keys(self):
        return requests.get(self.address).json()
