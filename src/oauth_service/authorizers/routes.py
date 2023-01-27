from typing import Any, Callable, Literal, Optional
from fastapi import APIRouter as FastAPIRouter, Query, status

from . import controller
from .schemas import OAuth2Client, ID


class APIRouter(FastAPIRouter):
    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        include_in_schema: bool = True,
        **kwargs: Any,
    ) -> None:
        path = path.removesuffix("/")
        slashed_path = f"{path}/"
        super().add_api_route(
            slashed_path, endpoint, include_in_schema=False, **kwargs
        )
        return super().add_api_route(
            path, endpoint, include_in_schema=include_in_schema, **kwargs
        )


router = APIRouter(prefix="/jobs")


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
)
async def inserts(data: OAuth2Client) -> ID:
    return await controller.insert(data)
