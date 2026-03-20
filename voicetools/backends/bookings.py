from typing import Protocol

from voicetools.utils import generate_booking_ref


class BookingBackend(Protocol):
    async def create_booking(
        self,
        shop_name: str,
        service: str,
        date: str,
        time: str,
        customer_name: str = "",
        car_info: str = "",
        phone: str = "",
    ) -> dict: ...

    async def get_bookings_by_phone(self, phone: str) -> list[dict]: ...

    async def get_bookings_by_shop_date(self, shop_name: str, date: str) -> list[dict]: ...


class MockBookingBackend:
    def __init__(self) -> None:
        self._bookings: dict[str, list[dict]] = {}
        self._slots: dict[tuple[str, str, str], str] = {}

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
        slot = (shop_name, date, time)
        if slot in self._slots:
            existing_ref = self._slots[slot]
            return {
                "error": f"Time slot already booked (ref {existing_ref}). Please choose a different time.",
                "conflict": True,
            }

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
        self._slots[slot] = ref
        if phone:
            self._bookings.setdefault(phone, []).append(booking)
        return booking

    async def get_bookings_by_phone(self, phone: str) -> list[dict]:
        return self._bookings.get(phone, [])

    async def get_bookings_by_shop_date(self, shop_name: str, date: str) -> list[dict]:
        all_bookings: list[dict] = []
        for bookings in self._bookings.values():
            for b in bookings:
                if b["shop_name"] == shop_name and b["date"] == date:
                    all_bookings.append(b)
        return all_bookings
