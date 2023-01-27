from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from oauth_middleware import LoginMiddleware, CognitoAuthorizer, ADAuthorizer

from . import database

from .config import Settings
from . import authorizers


def create_app():
    app = FastAPI(
        title="TagSonic API",
        description=description,
        version="0.0.1",
        terms_of_service="http://www.teialabs.com/",
        contact={
            "name": "Teia Labs",
            "url": "http://www.teialabs.com/",
            "email": "contato@teialabs.com",
        },
    )
    database.setup()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        expose_headers=['X-Secret-Param']
    )
    authorizers = [
        CognitoAuthorizer(region, userpool, app_client_id, token_type),
        ADAuthorizer(tenant, app_client_id, lambda _: (True, "")),
    ]
    app.add_middleware(
        LoginMiddleware,
        users={},
        admin_scope="TeiaMember",
        authorizers=authorizers,
    )

    app.include_router(authorizers.router)
    return app