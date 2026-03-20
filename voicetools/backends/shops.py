from typing import TYPE_CHECKING, Protocol

from voicetools.utils import SLOT_TIMES

if TYPE_CHECKING:
    from voicetools.backends.bookings import MockBookingBackend


class ShopBackend(Protocol):
    async def find_nearby_shops(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        address: str | None = None,
        date: str | None = None,
        service: str | None = None,
    ) -> list[dict]: ...


SEED_SHOPS = [
    {
        "name": "Elite Detail Studio",
        "location": "District 2, An Phu",
        "district": "District 2",
        "rating": 4.9,
        "specialty": "PPF and Porsche/Ferrari specialist",
        "services": ["PPF", "Full Detail", "Paint Correction", "Ceramic Coating", "Wash"],
        "hours": "8am-8pm Mon-Sun",
        "phone": "+84 28 1234 5678",
        "coords": {"lat": 10.7937, "lng": 106.7437},
    },
    {
        "name": "Prestige Auto Care",
        "location": "District 7, Phu My Hung",
        "district": "District 7",
        "rating": 4.8,
        "specialty": "German brands specialist",
        "services": ["Full Detail", "Engine Bay Clean", "Paint Protection", "Wash", "Tint"],
        "hours": "8am-7pm Mon-Sat",
        "phone": "+84 28 2345 6789",
        "coords": {"lat": 10.7280, "lng": 106.7010},
    },
    {
        "name": "Diamond Wash",
        "location": "Binh Thanh",
        "district": "Binh Thanh",
        "rating": 4.7,
        "specialty": "Express and 24/7 service",
        "services": ["Express Wash", "Interior Clean", "Full Detail", "Wax"],
        "hours": "24/7",
        "phone": "+84 28 3456 7890",
        "coords": {"lat": 10.8013, "lng": 106.7130},
    },
    {
        "name": "Saigon Pro Detailing",
        "location": "District 1, Ben Nghe",
        "district": "District 1",
        "rating": 4.8,
        "specialty": "Luxury sedans and paint correction",
        "services": ["Paint Correction", "Ceramic Coating", "Full Detail", "Wash", "Tint"],
        "hours": "8am-9pm Mon-Sun",
        "phone": "+84 28 4567 8901",
        "coords": {"lat": 10.7769, "lng": 106.7009},
    },
    {
        "name": "VIP Auto Spa",
        "location": "Tan Binh, Bay Hien",
        "district": "Tan Binh",
        "rating": 4.6,
        "specialty": "Japanese and Korean brands",
        "services": ["Wash", "Interior Clean", "Wax", "Full Detail", "Engine Bay Clean"],
        "hours": "7am-8pm Mon-Sun",
        "phone": "+84 28 5678 9012",
        "coords": {"lat": 10.7955, "lng": 106.6525},
    },
    {
        "name": "Lotus Car Spa",
        "location": "District 4, Khanh Hoi",
        "district": "District 4",
        "rating": 4.7,
        "specialty": "SUV and MPV specialist",
        "services": ["Full Detail", "PPF", "Wash", "Interior Clean", "Ceramic Coating"],
        "hours": "8am-8pm Mon-Sun",
        "phone": "+84 28 6789 0123",
        "coords": {"lat": 10.7588, "lng": 106.7012},
    },
    {
        "name": "Golden Shield Auto",
        "location": "Thu Duc, Linh Xuan",
        "district": "Thu Duc",
        "rating": 4.5,
        "specialty": "Paint protection film and wraps",
        "services": ["PPF", "Vinyl Wrap", "Ceramic Coating", "Wash", "Full Detail"],
        "hours": "8am-7pm Mon-Sat",
        "phone": "+84 28 7890 1234",
        "coords": {"lat": 10.8700, "lng": 106.7700},
    },
]


class MockShopBackend:
    def __init__(self, booking_backend: "MockBookingBackend | None" = None):
        self._booking_backend = booking_backend

    async def find_nearby_shops(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        address: str | None = None,
        date: str | None = None,
        service: str | None = None,
    ) -> list[dict]:
        shops = [
            dict(s) for s in SEED_SHOPS
            if not service or service in s["services"]
        ]
        if date and self._booking_backend:
            for shop in shops:
                booked = await self._booking_backend.get_bookings_by_shop_date(shop["name"], date)
                booked_times = {b["time"] for b in booked}
                shop["available_slots"] = [t for t in SLOT_TIMES if t not in booked_times]
                shop["fully_booked"] = len(shop["available_slots"]) == 0
        return shops
