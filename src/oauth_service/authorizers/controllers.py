from fastapi import status
from fastapi.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError

from .schemas import Authorization, ID, OAuth2Server


async def authorize(filters: dict, token: Authorization):
    pass


async def create(data: OAuth2Server) -> ID:
    try:
        res = data.insert_one()
    except DuplicateKeyError:
        s, msg = status.HTTP_409_CONFLICT, "Already exists."
        return HTTPException(status_code=s, detail=msg)
    return ID(id=res.inserted_id)


async def read_many(limit: int, skip: int) -> list[OAuth2Server]:
    return OAuth2Server.find(limit=limit, skip=skip)


async def delete_one(filters):
    return OAuth2Server.delete_one(filters)
