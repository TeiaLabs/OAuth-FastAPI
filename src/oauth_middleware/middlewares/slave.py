import time
from typing import List

from aioclient import get_request
from aioclient.exceptions import GetFailed
from fastapi import FastAPI, Request
from starlette.types import Receive, Scope, Send
from timed_dict import TimedDict

from ..utils import SlaveUserInfo as UserInfo
from ..utils import build_response
from ..utils.constants import (
    AUTHORIZATION_FAILED,
    MISSING_HEADER,
    TOKEN_EXPIRED,
)


class SlaveOAuthVerifier:
    def __init__(
        self,
        app: FastAPI,
        master_url: str,
        secret: str,
        users: TimedDict,
        ignored_paths: List[str],
    ):
        self.app = app
        self.master_url = master_url
        self.secret = secret
        self.users = users
        self.ignored_paths = ignored_paths

    async def get_user_info(
        self,
        request,
    ):
        user_key = request.session.get("user")
        if user_key is not None:
            user_info = self.users.get(user_key)
            if user_info is None:
                raise GetFailed("Impossible.")
            return user_info

        auth = request.headers.get("authorization")
        if auth is None:
            raise GetFailed(MISSING_HEADER)

        resp = await get_request(
            url=f"{self.master_url}/user_info/{auth}",
            headers=dict(secret=self.secret),
        )
        user_info = UserInfo(**resp)
        return user_info

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        path = scope["path"][scope["path"].find("/") :]
        if path in self.ignored_paths:
            return await self.app(scope, receive, send)

        request = Request(scope=scope, receive=receive, send=send)

        try:
            user_info = await self.get_user_info(request)

            self.users[user_info.key] = user_info
            request.session["user"] = user_info.key
            request.state.user = user_info

            if time.time() > user_info.expire_at:
                self.users.pop(user_info.key)
                return await build_response(
                    scope, receive, send, 401, TOKEN_EXPIRED
                )

            return await self.app(scope, receive, send)

        except GetFailed:
            return await build_response(
                scope, receive, send, 401, AUTHORIZATION_FAILED
            )
