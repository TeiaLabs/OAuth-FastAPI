from typing import Literal, Optional

from pydantic import BaseModel
from redb import Document, CompoundIndex

Secret = str


class DynamicArgs(Document):
    key: str
    value: str


class OAuth2Server(Document):
    client_id: Secret
    extra_args: Optional[list[DynamicArgs]] = None
    org: str
    provider: Literal["Cognito", "AD"]
    redirect_uri: str
    response_mode: Literal["code", "fragment"]
    response_type: Literal["token", "code"]
    scopes: list[str]
    tenant_id: Secret

    @classmethod
    def get_indices(cls) -> list[CompoundIndex]:
        indices = [
            CompoundIndex(field=[cls.org, cls.provider], unique=True),
        ]
        return super().get_indices().extend(indices)


class Authorization(BaseModel):
    access_token: str
    expires_in: int
    id_token: str
    refresh_token: str
    token_type: str

    @classmethod
    def from_jwt(cls, token: str):
        d = {
            "access_token": token,
            "expires_in": 3600,
            "id_token": token,
            "refresh_token": token,
            "token_type": "Bearer",
        }
        return cls(**d)


class ID(BaseModel):
    id: str
