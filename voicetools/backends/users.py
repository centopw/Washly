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
        "service_history": ["Full Detail - Jan 2025", "PPF - Nov 2024", "Ceramic Coating - Aug 2024"],
    },
    {
        "name": "Tran Thi Bich",
        "phone": "+84912345678",
        "car_make": "Mercedes",
        "car_model": "S-Class",
        "car_plate": "51B-67890",
        "tier": "Premium",
        "service_history": ["Full Detail - Feb 2025", "Paint Correction - Dec 2024"],
    },
    {
        "name": "Le Hoang Nam",
        "phone": "+84923456789",
        "car_make": "BMW",
        "car_model": "M5",
        "car_plate": "51C-11223",
        "tier": "Standard",
        "service_history": ["Wash - Mar 2025"],
    },
]

_phone_index: dict[str, dict] = {u["phone"]: u for u in SEED_USERS}


class MockUserBackend:
    async def get_user_by_phone(self, phone: str) -> dict | None:
        normalized = phone.replace(" ", "").replace("-", "")
        return _phone_index.get(normalized)
