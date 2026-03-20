from voicetools.backends.db import get_database
from voicetools.utils import SLOT_TIMES


class MongoShopBackend:
    async def find_nearby_shops(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        address: str | None = None,
        date: str | None = None,
        service: str | None = None,
    ) -> list[dict]:
        db = get_database()
        query: dict = {}
        if service:
            query["services"] = service
        if latitude is not None and longitude is not None:
            query["coords_geo"] = {
                "$nearSphere": {
                    "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                    "$maxDistance": 20000,
                }
            }
        cursor = db.shops.find(query, {"_id": 0})
        shops = await cursor.to_list(length=20)

        if date:
            for shop in shops:
                booked = await self._get_booked_times(shop["name"], date)
                shop["available_slots"] = [t for t in SLOT_TIMES if t not in booked]
                shop["fully_booked"] = len(shop["available_slots"]) == 0

        return shops

    async def _get_booked_times(self, shop_name: str, date: str) -> set[str]:
        db = get_database()
        cursor = db.bookings.find(
            {"shop_name": shop_name, "date": date},
            {"time": 1, "_id": 0},
        )
        docs = await cursor.to_list(length=100)
        return {d["time"] for d in docs}
