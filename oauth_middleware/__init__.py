from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .authorizers import AuthorizerType, ADAuthorizer, CognitoAuthorizer
from .middlewares import OAuthVerifier


AUTHORIZERS = {
    'azure': ADAuthorizer,
    'aws': CognitoAuthorizer
}


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
    auth_type = config["type"].lower()
    if auth_type not in AUTHORIZERS.keys():
        allowed_authorizers = '\n\t->'.join(AUTHORIZERS.keys())
        raise ValueError(f"Unknown authorizer type. Choose one of: {allowed_authorizers}")

    return AUTHORIZERS[auth_type](**config["config"])
