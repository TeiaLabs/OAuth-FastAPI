from typing import Dict

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from oauth_middleware import init_app

app = FastAPI()

init_app(app, {
    "authorizer": {
        "type": "aws", "config": {"region": "us-west-2", "user_pool": "us-west-2_1n3VTfnGQ"}
    }, "generator_routes": ["/"], "verifier_routes": ["/"], "session_config": {"ignore": True}})

app.add_middleware(
    SessionMiddleware,
    secret_key="notsafe",
    session_cookie="session",
    max_age=60 * 60,
    same_site="lax"
)


@app.get('/', response_model=Dict[str, str])
def test():
    return {'status': 'ok'}


if __name__ == '__main__':
    # Azure
    # https://docs.microsoft.com/pt-br/azure/active-directory/develop/v2-oauth-ropc

    uvicorn.run(app)
