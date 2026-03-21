from typing import Protocol

from voicetools.utils import generate_booking_ref

# Pre-seeded bookings — mix of past and upcoming slots
# Dates relative to 2026-03-21 (today)
SEED_BOOKINGS = [
    # --- Past bookings (for service history context) ---
    {
        "ref": "VAL-SEED0001",
        "shop_name": "Elite Detail Studio",
        "service": "PPF",
        "date": "2026-03-10",
        "time": "9am",
        "customer_name": "Pham Minh Duc",
        "car_info": "Ferrari Roma 51D-55678",
        "phone": "+84934567890",
    },
    {
        "ref": "VAL-SEED0002",
        "shop_name": "Prestige Auto Care",
        "service": "Full Detail",
        "date": "2026-03-15",
        "time": "10am",
        "customer_name": "Tran Thi Bich",
        "car_info": "Mercedes S-Class 51B-67890",
        "phone": "+84912345678",
    },
    {
        "ref": "VAL-SEED0003",
        "shop_name": "Diamond Wash",
        "service": "Wash",
        "date": "2026-03-18",
        "time": "8am",
        "customer_name": "Dang Van Thanh",
        "car_info": "Toyota Camry 51H-22334",
        "phone": "+84967890123",
    },
    # --- Upcoming bookings ---
    # 2026-03-22 (Sunday) — Elite Detail Studio partially booked
    {
        "ref": "VAL-SEED0004",
        "shop_name": "Elite Detail Studio",
        "service": "Ceramic Coating",
        "date": "2026-03-22",
        "time": "9am",
        "customer_name": "Nguyen Van An",
        "car_info": "Porsche 911 Carrera 51A-12345",
        "phone": "+84901234567",
    },
    {
        "ref": "VAL-SEED0005",
        "shop_name": "Elite Detail Studio",
        "service": "Paint Correction",
        "date": "2026-03-22",
        "time": "11am",
        "customer_name": "Hoang Thi Lan",
        "car_info": "Lexus RX 350 51F-33412",
        "phone": "+84945678901",
    },
    # 2026-03-22 (Sunday) — Prestige Auto Care one booking
    {
        "ref": "VAL-SEED0006",
        "shop_name": "Prestige Auto Care",
        "service": "Engine Bay Clean",
        "date": "2026-03-22",
        "time": "10am",
        "customer_name": "Le Hoang Nam",
        "car_info": "BMW M5 51C-11223",
        "phone": "+84923456789",
    },
    # 2026-03-23 (Monday) — Saigon Pro Detailing busy morning
    {
        "ref": "VAL-SEED0007",
        "shop_name": "Saigon Pro Detailing",
        "service": "Full Detail",
        "date": "2026-03-23",
        "time": "8am",
        "customer_name": "Vo Quoc Hung",
        "car_info": "Range Rover Sport 51G-78901",
        "phone": "+84956789012",
    },
    {
        "ref": "VAL-SEED0008",
        "shop_name": "Saigon Pro Detailing",
        "service": "Tint",
        "date": "2026-03-23",
        "time": "9am",
        "customer_name": "Dang Van Thanh",
        "car_info": "Toyota Camry 51H-22334",
        "phone": "+84967890123",
    },
    {
        "ref": "VAL-SEED0009",
        "shop_name": "Saigon Pro Detailing",
        "service": "Paint Correction",
        "date": "2026-03-23",
        "time": "10am",
        "customer_name": "Tran Thi Bich",
        "car_info": "Mercedes S-Class 51B-67890",
        "phone": "+84912345678",
    },
    # 2026-03-24 (Tuesday) — Lotus Car Spa one booking
    {
        "ref": "VAL-SEED0010",
        "shop_name": "Lotus Car Spa",
        "service": "PPF",
        "date": "2026-03-24",
        "time": "2pm",
        "customer_name": "Pham Minh Duc",
        "car_info": "Ferrari Roma 51D-55678",
        "phone": "+84934567890",
    },
    # 2026-03-25 (Wednesday) — VIP Auto Spa two bookings
    {
        "ref": "VAL-SEED0011",
        "shop_name": "VIP Auto Spa",
        "service": "Wash",
        "date": "2026-03-25",
        "time": "8am",
        "customer_name": "Hoang Thi Lan",
        "car_info": "Lexus RX 350 51F-33412",
        "phone": "+84945678901",
    },
    {
        "ref": "VAL-SEED0012",
        "shop_name": "VIP Auto Spa",
        "service": "Interior Clean",
        "date": "2026-03-25",
        "time": "11am",
        "customer_name": "Nguyen Van An",
        "car_info": "Porsche 911 Carrera 51A-12345",
        "phone": "+84901234567",
    },
    # 2026-03-28 (Saturday) — Golden Shield fully booked (PPF day)
    {
        "ref": "VAL-SEED0013",
        "shop_name": "Golden Shield Auto",
        "service": "PPF",
        "date": "2026-03-28",
        "time": "8am",
        "customer_name": "Nguyen Van An",
        "car_info": "Porsche 911 Carrera 51A-12345",
        "phone": "+84901234567",
    },
    {
        "ref": "VAL-SEED0014",
        "shop_name": "Golden Shield Auto",
        "service": "Vinyl Wrap",
        "date": "2026-03-28",
        "time": "9am",
        "customer_name": "Le Hoang Nam",
        "car_info": "BMW M5 51C-11223",
        "phone": "+84923456789",
    },
    {
        "ref": "VAL-SEED0015",
        "shop_name": "Golden Shield Auto",
        "service": "Ceramic Coating",
        "date": "2026-03-28",
        "time": "10am",
        "customer_name": "Vo Quoc Hung",
        "car_info": "Range Rover Sport 51G-78901",
        "phone": "+84956789012",
    },
]


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

    async def cancel_booking(self, ref: str) -> dict: ...

    async def get_booking_by_ref(self, ref: str) -> dict | None: ...


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

    async def get_booking_by_ref(self, ref: str) -> dict | None:
        for bookings in self._bookings.values():
            for b in bookings:
                if b["ref"] == ref:
                    return b
        return None

    async def cancel_booking(self, ref: str) -> dict:
        booking = await self.get_booking_by_ref(ref)
        if not booking:
            return {"error": f"Booking {ref} not found."}
        slot = (booking["shop_name"], booking["date"], booking["time"])
        self._slots.pop(slot, None)
        phone = booking.get("phone", "")
        if phone and phone in self._bookings:
            self._bookings[phone] = [b for b in self._bookings[phone] if b["ref"] != ref]
        return {"cancelled": True, "ref": ref}
