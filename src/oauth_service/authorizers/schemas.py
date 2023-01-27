from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class OAuth2Client(BaseModel):
    app_id: str
    client_id: str
    redirect_uri: str
    response_mode: Literal["code", "fragment"]
    response_type: Literal["token", "code"]
    scopes: list[str]


class ID(BaseModel):
    id: str
