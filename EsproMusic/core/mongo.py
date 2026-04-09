from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI
from ..logging import LOGGER

LOGGER(__name__).info("connecting to your mongo database...")

try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)

    # main database
    mongodb = _mongo_async_.Anon

    # ================= collections =================
    groups = mongodb.groups          # nsfw toggle per chat
    NSFW = mongodb.nsfw              # scan cache
    NSFW_STORAGE = mongodb.nsfw_storage  # optional storage/logging

    LOGGER(__name__).info("connected to your mongo database.")

except Exception as e:
    LOGGER(__name__).error(f"failed to connect to your mongo database: {e}")
    exit()
