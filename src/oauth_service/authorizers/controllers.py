from fastapi import status
from fastapi.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError

from .schemas import ID, OAuth2Client


async def create(data: OAuth2Client) -> ID:
    try:
        res = data.insert_one()
    except DuplicateKeyError:
        s, msg = status.HTTP_409_CONFLICT, "Already exists."
        return HTTPException(status_code=s, detail=msg)
    return ID(id=res.inserted_id)


async def read_many(limit: int, skip: int) -> list[OAuth2Client]:
    return OAuth2Client.find(limit=limit, skip=skip)


