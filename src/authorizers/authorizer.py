import abc
from typing import Tuple


class Authorizer(metaclass=abc.ABCMeta):
    ALGORITHMS = [
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
        "ES256",
        "ES384",
        "ES512",
        "PS256",
        "PS384",
        "PS512"
    ]

    @abc.abstractmethod
    def validate_access_token(self, token: str) -> Tuple[bool, str]:
        raise NotImplementedError
