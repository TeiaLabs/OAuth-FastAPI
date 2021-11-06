import abc
from typing import Optional


class Authorizer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_access_token(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def verify_access_token(self, token: str) -> Optional[str]:
        raise NotImplementedError
