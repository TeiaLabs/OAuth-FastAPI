import secrets
from typing import Optional
from typing import Tuple

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import UJSONResponse
from jose import jwt
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from timed_dict import TimedDict

from ..authorizers import ADAuthorizer
from ..authorizers import AuthorizerType
from ..authorizers import CognitoAuthorizer
from ..utils import build_response
from ..utils import MasterUserInfo as UserInfo
from ..utils.constants import AUTHENTICATOR_NOT_PROVIDED
from ..utils.constants import METHOD_NOT_ALLOWED
from ..utils.constants import UNKNOWN_AUTHENTICATOR


class LoginMiddleware:
    def __init__(self, app: FastAPI, users: TimedDict, admin_scope: str):
        self.app = app
        self.users = users
        self.admin_scope = admin_scope

    async def logon(self, scope: Scope, receive: Receive, send: Send):
        if scope["method"] != "POST":
            return await build_response(
                scope, receive, send, 405, METHOD_NOT_ALLOWED
            )

        request = Request(scope=scope, receive=receive, send=send)
        body = await request.json()

        resp, authorizer = await self.get_authorizer(body)
        if authorizer is None:
            return await build_response(
                scope, receive, send, 400, resp
            )

        headers = request.headers
        token = headers.get("authentication")
        is_valid, msg = authorizer.validate_token(token)
        if not is_valid:
            return await build_response(scope, receive, send, 400, msg)

        claims = await self.get_claims(resp, token)
        key = secrets.token_urlsafe(12)

        request.session["user"] = key
        user = await self.save_user(resp, body, claims)
        self.users[key] = UserInfo.from_claims(key, user.id, claims)

        response = UJSONResponse(status_code=200, content=dict(key=key))
        return await response(scope, receive, send)

    async def get_claims(self, authenticator, token):
        claims = jwt.get_unverified_claims(token)
        if authenticator == "ad":
            authorizer_identifier = claims["oid"]
            scope = int(self.admin_scope in claims["roles"].split(" "))
        else:
            authorizer_identifier = claims["sub"]
            scope = int(self.admin_scope in claims["scope"].split(" "))

        return dict(
            authorizer_identifier=authorizer_identifier,
            expire_at=claims["exp"],
            scope=scope,
            issuer=claims["iss"]
        )

    @staticmethod
    async def get_authorizer(body) -> Tuple[str, Optional[AuthorizerType]]:
        try:
            authenticator = body.pop("authenticator")
        except KeyError:
            return AUTHENTICATOR_NOT_PROVIDED, None

        if authenticator.lower() == "ad":
            authorizer = ADAuthorizer(**body)
        elif authenticator.lower() == "cognito":
            authorizer = CognitoAuthorizer(**body)
        else:
            return UNKNOWN_AUTHENTICATOR, None

        return authenticator, authorizer

    @staticmethod
    async def save_user(authorizer, body, claims):
        raise NotImplementedError

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        paths = scope["path"].split("/")
        if paths[-1] == "logon":
            return await self.logon(scope, receive, send)

        return await self.app(scope, receive, send)
