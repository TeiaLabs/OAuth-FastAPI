from redb import RedB
from redb.mongo_system import MongoConfig

from .config import Settings


def setup() -> None:
    RedB.setup(config=MongoConfig(database_uri=Settings.env.mongodb_uri))
