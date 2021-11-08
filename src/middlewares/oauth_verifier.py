from typing import List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from ..authorizers import AuthorizerType


class OAuthVerifier:
    def __init__(self, app: ASGIApp, authorizer: AuthorizerType, routes: List[str]):
        self.app = app
        self.authorizer = authorizer
        self.routes = routes

        self.session_token_map = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["path"] not in self.routes:
            return await self.app(scope, receive, send)

        req = Request(scope, receive=receive, send=send)
        session_id = req.session.get('session-id')
        if session_id is None:
            resp = JSONResponse(status_code=401, content={"message": "User is not authenticated"})
            return await resp(scope, receive, send)

        token = self.authorizer.validate_access_token(self.session_token_map[session_id])
        if token is None:
            resp = JSONResponse(status_code=403, content={"message": "User does not have enough privileges"})
            return await resp(scope, receive, send)

        req.state.token = token

        return await self.app(scope, receive, send)
