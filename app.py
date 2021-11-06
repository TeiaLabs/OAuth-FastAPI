from typing import Dict

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src import init_app

app = FastAPI()

init_app(app, {"authorizer": {"type": "Azure", "config": {}}, "generator_routes": ["/"], "verifier_routes": ["/"]})


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
    uvicorn.run(app)
