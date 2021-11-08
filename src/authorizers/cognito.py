import time
from typing import Tuple

import requests
from jose import jwk
from jose import jwt
from jose.utils import base64url_decode

from .authorizer import Authorizer
from ..utils.cache import timed_cache


class CognitoAuthorizer(Authorizer):
    def __init__(self, app_client_id, region, user_pool, token_validator):
        self.app_client_id = app_client_id
        self.address = f"https://cognito-idp.{region}.amazonaws.com/{user_pool}/.well-known/jwks.json"
        self.token_validator = token_validator if token_validator else lambda _: True

    def validate_access_token(self, token: str) -> Tuple[bool, str]:
        if not self._verify_signing_key(token):
            return False, ""

        if not self._verify_claims(token):
            return False, ""

        return True, ""

    def _verify_signing_key(self, token):
        key = self._get_signing_key(token)

        public_key = jwk.construct(key)
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

        if not public_key.verify(message.encode("utf8"), decoded_signature):
            return False

        return True

    def _verify_claims(self, token):
        claims = jwt.get_unverified_claims(token)
        if time.time() > claims['exp']:
            return False

        if claims['aud'] != self.app_client_id:
            return False

        return True

    def _get_signing_key(self, token):
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]

        keys = self._get_keys()
        for key in keys["keys"]:
            if key['kid'] == kid:
                return key

        return None

    @timed_cache(3600)
    def _get_keys(self):
        return requests.get(self.address).json()
