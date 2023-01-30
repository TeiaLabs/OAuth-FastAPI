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
    status_code=status.HTTP_201_CREATED,
)
async def create(data: OAuth2Client) -> ID:
    return await controller.create(data)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def read_many(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
) -> list[OAuth2Client]:
    return await controller.read(limit, skip)


@router.delete(
    "/{identifier}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_all(identifier: str) -> None:
    return await controller.delete(filter={"identifier": identifier})
