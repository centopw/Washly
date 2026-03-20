from voicetools.backends.db import get_database


class MongoUserBackend:
    async def get_user_by_phone(self, phone: str) -> dict | None:
        db = get_database()
        normalized = phone.replace(" ", "").replace("-", "")
        user = await db.users.find_one({"phone": normalized}, {"_id": 0})
        return user
