from fastapi.responses import UJSONResponse
from starlette.types import Receive, Scope, Send


async def build_response(
    scope: Scope, receive: Receive, send: Send, status_code: int, message: str
):
    response = UJSONResponse(
        status_code=status_code, content=dict(details=message)
    )
    return await response(scope, receive, send)
