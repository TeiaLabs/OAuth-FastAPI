from typing import Literal

from pydantic import BaseModel
from redb import Document

Secret = str


class OAuth2Server(Document):
    app_id: Secret
    client_id: Secret
    org: str
    provider: Literal["Cognito", "AD"]
    redirect_uri: str
    response_mode: Literal["code", "fragment"]
    response_type: Literal["token", "code"]
    scopes: list[str]
    uri_template: str


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
