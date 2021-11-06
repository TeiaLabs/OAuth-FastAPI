import uuid
from typing import List

from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from ..authorizers import AuthorizerType


class OAuthGenerator:
    def __init__(self, app: ASGIApp, authorizer: AuthorizerType, routes: List[str]):
        self.app = app
        self.authorizer = authorizer
        self.routes = routes

        self.verifier = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["path"] not in self.routes:
            return await self.app(scope, receive, send)

        req = Request(scope, receive=receive, send=send)

        token = self.authorizer.get_access_token(await req.json())
        if token is None:
            resp = JSONResponse(status_code=401, content={"message": "Token generation failed"})
            return await resp(scope, receive, send)

        session_id = uuid.uuid4().hex
        req.session["session-id"] = session_id
        self.verifier.session_token_map[session_id] = token

        req.state.token = token

        return await self.app(scope, receive, send)
