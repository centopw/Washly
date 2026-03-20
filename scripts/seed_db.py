"""Seed demo data into MongoDB. Run with: uv run python -m scripts.seed_db"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from voicetools.backends.shops import SEED_SHOPS
from voicetools.backends.users import SEED_USERS
from voicetools.config import settings


async def seed() -> None:
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]

    for shop in SEED_SHOPS:
        doc = dict(shop)
        doc["coords_geo"] = {
            "type": "Point",
            "coordinates": [shop["coords"]["lng"], shop["coords"]["lat"]],
        }
        await db.shops.update_one(
            {"name": shop["name"]},
            {"$set": doc},
            upsert=True,
        )
        print(f"Upserted shop: {shop['name']}")

    for user in SEED_USERS:
        await db.users.update_one(
            {"phone": user["phone"]},
            {"$set": user},
            upsert=True,
        )
        print(f"Upserted user: {user['name']}")

    await db.shops.create_index([("coords_geo", "2dsphere")])
    await db.users.create_index("phone", unique=True)
    await db.bookings.create_index([("shop_name", 1), ("date", 1), ("time", 1)], unique=True)
    await db.bookings.create_index("phone")
    await db.bookings.create_index("ref", unique=True)
    print("Indexes ensured.")

    client.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
