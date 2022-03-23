import time

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.requests import Request
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from timed_dict import TimedDict

from ..utils import build_response
from ..utils.constants import METHOD_NOT_ALLOWED
from ..utils.constants import TOKEN_EXPIRED
from ..utils.constants import UNAUTHORIZED
from ..utils.constants import USER_NOT_AUTHENTICATED


class MasterOAuthVerifier:
    def __init__(self, app: FastAPI, secret: str, users: TimedDict):
        self.app = app
        self.secret = secret
        self.users = users

    async def process_user_info_request(
            self, scope: Scope, receive: Receive, send: Send, key: str
    ):
        if scope["method"] != "GET":
            return await build_response(
                scope, receive, send, 405, METHOD_NOT_ALLOWED
            )

        request = Request(scope=scope, receive=receive, send=send)
        headers = request.headers

        secret = headers.get("secret")
        if secret != self.secret:
            return await build_response(
                scope, receive, send, 401, UNAUTHORIZED
            )

        user = self.users.get(key)
        if user is None:
            return await build_response(
                scope, receive, send, 404, USER_NOT_AUTHENTICATED
            )

        elif time.time() > user.expire_at:
            return await build_response(
                scope, receive, send, 401, TOKEN_EXPIRED
            )

        response = UJSONResponse(
            status_code=200, content=dict(
                authorizer_identifier=user.authorizer_identifier,
                expire_at=user.expire_at,
                key=user.key,
                scope=user.scope,
            )
        )
        return await response(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        paths = scope["path"].split("/")
        if paths[-2] == "user_info":
            return await self.process_user_info_request(scope, receive, send, paths[-1])

        request = Request(scope=scope, receive=receive, send=send)

        secret_header = request.headers.get("secret")
        if secret_header is not None and secret_header == self.secret:
            user_key = request.headers.get("authentication")
        else:
            user_key = request.session.get("user")

        if user_key is None:
            return await build_response(
                scope, receive, send, 401, USER_NOT_AUTHENTICATED
            )

        user_info = self.users.get(user_key)
        if user_info is None:
            return await build_response(
                scope, receive, send, 401, TOKEN_EXPIRED
            )

        if time.time() > user_info.expire_at:
            if user_info.key in self.users:
                self.users.pop(user_info.key)

            return await build_response(scope, receive, send, 401, TOKEN_EXPIRED)

        request.state.user = user_info
        return await self.app(scope, receive, send)
