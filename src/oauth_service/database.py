from pathlib import Path

from redb import RedB
from redb.interface.configs import JSONConfig

from .config import Settings


def setup() -> None:
    # RedB.setup(config=MongoConfig(database_uri=Settings.env.mongodb_uri)
    RedB.setup(config=JSONConfig(client_folder_path=Path("./tmp/db")))
