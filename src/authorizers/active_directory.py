from typing import Optional

from .authorizer import Authorizer


class ADAuthorizer(Authorizer):
    def __init__(self, **kwargs):
        pass

    def get_access_token(self, *args, **kwargs) -> str:
        pass

    def verify_access_token(self, token: str) -> Optional[str]:
        pass
