from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI
from ..logging import LOGGER

LOGGER(__name__).info("💮 connecting to mongodb...")

try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)

    # ================= DATABASE =================
    # you can change DB name in config later if needed
    mongodb = _mongo_async_.EsproMusic

    # ================= COLLECTIONS =================
    groups = mongodb.groups              # group settings (nsfw, locks, etc.)
    nsfw_cache = mongodb.nsfw            # scan cache (avoid repeated API calls)
    nsfw_storage = mongodb.nsfw_storage  # optional: flagged media storage/logs
    log_db = mongodb.log_channel
    LOGGER(__name__).info("💮 mongodb connected successfully.")

except Exception as e:
    LOGGER(__name__).error(f"💮 mongodb connection failed: {e}")
    _mongo_async_ = None
    mongodb = None
    groups = None
    nsfw_cache = None
    nsfw_storage = None
