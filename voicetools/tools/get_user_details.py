from loguru import logger

from voicetools.backends.provider import get_user_backend


async def handle(params) -> None:
    args = params.arguments
    phone = args.get("phone_number", "").strip()

    # Normalize Vietnamese local format
    if phone.startswith("0"):
        phone = "+84" + phone[1:]

    last_four = phone[-4:] if len(phone) >= 4 else phone
    logger.info("get_user_details lookup for ...{}", last_four)

    backend = get_user_backend()
    user = await backend.get_user_by_phone(phone)

    if not user:
        await params.result_callback(
            "NEW_CUSTOMER: No account found for this phone number. "
            "This is their first time using our service. "
            "Welcome them warmly as a first-time customer. "
            "Collect their name and car details naturally during the booking process."
        )
        return

    history = user.get("service_history", [])
    last_service = f" Last service: {history[-1]}." if history else ""
    result = (
        f"RETURNING_CUSTOMER: Found {user['name']}, {user['tier']} member, "
        f"driving a {user['car_make']} {user['car_model']} ({user.get('car_plate', '')}).{last_service} "
        f"Do not ask for their name, phone, or car details again."
    )
    await params.result_callback(result)
