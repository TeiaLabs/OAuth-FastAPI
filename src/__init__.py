from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .authorizers import AuthorizerType, ADAuthorizer, CognitoAuthorizer
from .middlewares import OAuthVerifier


def init_app(app: FastAPI, config: dict) -> None:
    authorizer = get_authorizer(config["authorizer"])

    app.add_middleware(OAuthVerifier, authorizer=authorizer, routes=config["verifier_routes"])

    for i in range(len(app.user_middleware)):
        if isinstance(app.user_middleware[i], SessionMiddleware):
            app.user_middleware.insert(0, app.user_middleware.pop(i))
            return

    if config["session_config"].get("ignore") is None:
        app.add_middleware(SessionMiddleware, **config["session_config"])


def get_authorizer(config: dict) -> AuthorizerType:
    if config["type"] == "Azure":
        return ADAuthorizer(**config["config"])
    elif config["type"] == "Amazon":
        return CognitoAuthorizer(**config["config"])
    raise ValueError("Unkown authorizer type. Choose one of:\n\t->Azure\n\t->Amazon")
