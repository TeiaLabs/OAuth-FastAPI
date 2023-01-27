from pydantic import BaseSettings


class AppSettings(BaseSettings):
    debug: bool = False
    mongodb_uri: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"


class Settings:
    env = AppSettings()
