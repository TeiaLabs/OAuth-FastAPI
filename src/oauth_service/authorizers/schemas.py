from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from redb import Document

Secret = str


class OAuth2Client(Document):
    app_id: Secret
    client_id: Secret
    org: str
    provider: str
    redirect_uri: str
    response_mode: Literal["code", "fragment"]
    response_type: Literal["token", "code"]
    scopes: list[str]


class ID(BaseModel):
    id: str
