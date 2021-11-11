from typing import List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from ..authorizers import AuthorizerType


class OAuthVerifier:
    def __init__(self, app: ASGIApp, authorizer: AuthorizerType, bearer: bool, routes: List[str]):
        self.app = app
        self.authorizer = authorizer
        self.bearer = bearer
        self.routes = routes

        self.session_token_map = {}

    async def header_flow(self, token, req, scope, receive, send):
        if self.bearer:
            token = token.split("Bearer ")[0]

        is_valid, msg = self.authorizer.validate_access_token(token)
        if not is_valid:
            resp = JSONResponse(status_code=401, content={"message": msg})
            return await resp(scope, receive, send)

        req.state.token = token
        return await self.app(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["path"] not in self.routes:
            return await self.app(scope, receive, send)

        req = Request(scope, receive=receive, send=send)

        authorization_header = req.headers["authorization"]
        if authorization_header is not None:
            return await self.header_flow(authorization_header, req, scope, receive, send)

        session_id = req.session.get('session-id')
        if session_id is not None:
            return await self.header_flow(self.session_token_map[session_id], req, scope, receive, send)

        resp = JSONResponse(status_code=401, content={"message": "User is not authorized"})
        return await resp(scope, receive, send)
