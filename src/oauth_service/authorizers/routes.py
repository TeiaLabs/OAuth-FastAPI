from typing import Any, Callable, Literal, Optional
from fastapi import APIRouter as FastAPIRouter, Query, status, Header

from . import controllers
from .schemas import Authorization, ID, OAuth2Server


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


router = APIRouter()


@router.post(
    "/orgs/{identifier}/providers/",
    status_code=status.HTTP_201_CREATED,
)
async def create(data: OAuth2Server) -> ID:
    return await controllers.create(data)


@router.get(
    "/orgs/{identifier}/providers/",
    status_code=status.HTTP_200_OK,
)
async def read_many(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
) -> list[OAuth2Server]:
    return await controllers.read_many(limit, skip)


@router.delete(
    "/orgs/{org_id}/providers/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_one(org_id: str, provider_id: str) -> None:
    f = {"org": org_id, "provider": provider_id}
    return await controllers.delete(filters=f)


@router.post(
    "/orgs/{org_id}/providers/{provider_id}/authorize",
    status_code=status.HTTP_200_OK,
)
async def authorize(
    org_id: str,
    provider_id: str,
    authorization: Optional[str] = Header(None),
):
    """
    Validate authorization header against provider.

    Return access token, refresh token, and expiration time.
    """
    f = {"org": org_id, "provider": provider_id}
    auth_data = Authorization.from_jwt(authorization)
    return await controllers.authorize(f, auth_data)
