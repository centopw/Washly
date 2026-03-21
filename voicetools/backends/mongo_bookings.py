from voicetools.backends.db import get_database
from voicetools.utils import generate_booking_ref


class MongoBookingBackend:
    async def create_booking(
        self,
        shop_name: str,
        service: str,
        date: str,
        time: str,
        customer_name: str = "",
        car_info: str = "",
        phone: str = "",
    ) -> dict:
        db = get_database()
        ref = generate_booking_ref()
        booking = {
            "ref": ref,
            "shop_name": shop_name,
            "service": service,
            "date": date,
            "time": time,
            "customer_name": customer_name,
            "car_info": car_info,
            "phone": phone,
        }
        try:
            await db.bookings.insert_one(booking)
        except Exception as e:
            if "duplicate key" in str(e).lower():
                existing = await db.bookings.find_one(
                    {"shop_name": shop_name, "date": date, "time": time}
                )
                existing_ref = existing["ref"] if existing else "unknown"
                return {
                    "error": f"Time slot already booked (ref {existing_ref}). Please choose a different time.",
                    "conflict": True,
                }
            raise
        booking.pop("_id", None)
        return booking

    async def get_bookings_by_phone(self, phone: str) -> list[dict]:
        db = get_database()
        cursor = db.bookings.find({"phone": phone}, {"_id": 0})
        return await cursor.to_list(length=100)

    async def get_bookings_by_shop_date(self, shop_name: str, date: str) -> list[dict]:
        db = get_database()
        cursor = db.bookings.find({"shop_name": shop_name, "date": date}, {"_id": 0})
        return await cursor.to_list(length=100)

    async def get_booking_by_ref(self, ref: str) -> dict | None:
        db = get_database()
        return await db.bookings.find_one({"ref": ref}, {"_id": 0})

    async def cancel_booking(self, ref: str) -> dict:
        db = get_database()
        result = await db.bookings.delete_one({"ref": ref})
        if result.deleted_count == 0:
            return {"error": f"Booking {ref} not found."}
        return {"cancelled": True, "ref": ref}
