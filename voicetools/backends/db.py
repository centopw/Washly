from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from voicetools.config import settings

_client: AsyncIOMotorClient | None = None


def get_database() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client[settings.mongodb_database]


async def ensure_indexes() -> None:
    db = get_database()
    await db.shops.create_index([("coords", "2dsphere")])
    await db.users.create_index("phone", unique=True)
    await db.bookings.create_index([("shop_name", 1), ("date", 1), ("time", 1)], unique=True)
    await db.bookings.create_index("phone")
    await db.bookings.create_index("ref", unique=True)


async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
