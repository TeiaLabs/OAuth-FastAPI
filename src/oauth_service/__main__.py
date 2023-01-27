import uvicorn

from .config import Settings


uvicorn.run(
    app='oauth_service.app:create_app',
    factory=True,
    reload=False,
    port=Settings.env.api_port,
    host=Settings.env.api_host,
)