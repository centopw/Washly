from typing import Protocol


class UserBackend(Protocol):
    async def get_user_by_phone(self, phone: str) -> dict | None: ...


SEED_USERS = [
    {
        "name": "Nguyen Van An",
        "phone": "+84901234567",
        "car_make": "Porsche",
        "car_model": "911 Carrera",
        "car_plate": "51A-12345",
        "tier": "VIP",
        "service_history": ["Full Detail - Jan 2026", "PPF - Nov 2025", "Ceramic Coating - Aug 2025"],
    },
    {
        "name": "Tran Thi Bich",
        "phone": "+84912345678",
        "car_make": "Mercedes",
        "car_model": "S-Class",
        "car_plate": "51B-67890",
        "tier": "Premium",
        "service_history": ["Full Detail - Feb 2026", "Paint Correction - Dec 2025"],
    },
    {
        "name": "Le Hoang Nam",
        "phone": "+84923456789",
        "car_make": "BMW",
        "car_model": "M5",
        "car_plate": "51C-11223",
        "tier": "Standard",
        "service_history": ["Wash - Mar 2026"],
    },
    {
        "name": "Pham Minh Duc",
        "phone": "+84934567890",
        "car_make": "Ferrari",
        "car_model": "Roma",
        "car_plate": "51D-55678",
        "tier": "VIP",
        "service_history": ["PPF - Feb 2026", "Full Detail - Jan 2026", "Paint Correction - Oct 2025"],
    },
    {
        "name": "Hoang Thi Lan",
        "phone": "+84945678901",
        "car_make": "Lexus",
        "car_model": "RX 350",
        "car_plate": "51F-33412",
        "tier": "Premium",
        "service_history": ["Ceramic Coating - Jan 2026", "Full Detail - Sep 2025"],
    },
    {
        "name": "Vo Quoc Hung",
        "phone": "+84956789012",
        "car_make": "Land Rover",
        "car_model": "Range Rover Sport",
        "car_plate": "51G-78901",
        "tier": "Premium",
        "service_history": ["Full Detail - Mar 2026", "Interior Clean - Jan 2026"],
    },
    {
        "name": "Dang Van Thanh",
        "phone": "+84967890123",
        "car_make": "Toyota",
        "car_model": "Camry",
        "car_plate": "51H-22334",
        "tier": "Standard",
        "service_history": ["Wash - Feb 2026"],
    },
]

_phone_index: dict[str, dict] = {u["phone"]: u for u in SEED_USERS}


class MockUserBackend:
    async def get_user_by_phone(self, phone: str) -> dict | None:
        normalized = phone.replace(" ", "").replace("-", "")
        return _phone_index.get(normalized)
