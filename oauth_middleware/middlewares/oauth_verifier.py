from typing import List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from ..authorizers import AuthorizerType
from ..utils.constants import AUTOBOTS
from ..utils.constants import BEARER
from ..utils.constants import DECEPTICONS
from ..utils.constants import INVALID_BEARER
from ..utils.constants import SKYNET
from ..utils.constants import TOKEN_NOT_PROVIDED


async def error_response(msg, scope, receive, send):
    resp = JSONResponse(status_code=401, content={"message": msg})
    return await resp(scope, receive, send)


class OAuthVerifier:
    def __init__(self, app: ASGIApp, authorizer: AuthorizerType, routes: List[str]):
        self.app = app
        self.authorizer = authorizer
        self.routes = routes

        self.session_token_map = {}

    async def header_flow(self, token, req, scope, receive, send):
        try:
            bearer_str, token = token.split(" ")
            bearer_str = bearer_str.lower()
            if bearer_str != BEARER:
                if bearer_str == "skynet":
                    return await error_response(SKYNET, scope, receive, send)
                elif bearer_str == "autobots":
                    return await error_response(AUTOBOTS, scope, receive, send)
                elif bearer_str == "decepticons":
                    return await error_response(DECEPTICONS, scope, receive, send)

                return await error_response(INVALID_BEARER, scope, receive, send)
        except ValueError:
            return await error_response(INVALID_BEARER, scope, receive, send)

        is_valid, msg = self.authorizer.validate_access_token(token)
        if not is_valid:
            return await error_response(msg, scope, receive, send)

        req.state.token = token
        return await self.app(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["path"] not in self.routes:
            return await self.app(scope, receive, send)

        req = Request(scope, receive=receive, send=send)

        authorization_header = req.headers.get("authorization")
        if authorization_header is not None:
            return await self.header_flow(authorization_header, req, scope, receive, send)

        session_id = req.session.get('session-id')
        if session_id is not None:
            return await self.header_flow(self.session_token_map[session_id], req, scope, receive, send)

        return await error_response(TOKEN_NOT_PROVIDED, scope, receive, send)
