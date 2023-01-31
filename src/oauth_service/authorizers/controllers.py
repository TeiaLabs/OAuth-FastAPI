from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from jose import jwt
from pymongo.errors import DuplicateKeyError

from oauth_middleware import CognitoAuthorizer

from .schemas import Authorization, ID, OAuth2Server


async def get_claims(authenticator, token, admin_scope: str):
    claims = jwt.get_unverified_claims(token)
    if authenticator == "ad":
        authorizer_identifier = claims["oid"]
        scope = int(admin_scope in claims["roles"].split(" "))
    else:
        authorizer_identifier = claims["sub"]
        scope = int(admin_scope in claims["scope"].split(" "))

    return dict(
        authorizer_identifier=authorizer_identifier,
        expire_at=claims["exp"],
        scope=scope,
        issuer=claims["iss"],
    )


async def authorize(filters: dict, auth_data: Authorization):
    if auth_data.access_token is None:
        return RedirectResponse(url="w")
    server = await read_one(filters)
    if server.provider != "cognito":
        s, msg = status.HTTP_401_UNAUTHORIZED, "Invalid provider."
        return HTTPException(status_code=s, detail=msg)
    auth_engine = CognitoAuthorizer(
        token_type=server.response_type,
        user_pool=server.tenant_id,
        app_client_id=server.client_id,
        **{item.key: item.value for item in server.extra_args},
    )
    success, msg = auth_engine.validate_token(auth_data.access_token)
    if not success:
        return RedirectResponse(url="w")


async def create(data: OAuth2Server) -> ID:
    try:
        res = data.insert_one()
    except DuplicateKeyError:
        s, msg = status.HTTP_409_CONFLICT, "Already exists."
        return HTTPException(status_code=s, detail=msg)
    return ID(id=res.inserted_id)


async def read_many(limit: int, skip: int) -> list[OAuth2Server]:
    return OAuth2Server.find(limit=limit, skip=skip)


async def read_one(filters: dict) -> OAuth2Server:
    item = OAuth2Server.find_one(filters)
    if not item:
        s = (status.HTTP_404_NOT_FOUND,)
        msg = f"Document not found with filters={filters}."
        return HTTPException(status_code=s, detail=msg)
    return item


async def delete_one(filters):
    return OAuth2Server.delete_one(filters)
