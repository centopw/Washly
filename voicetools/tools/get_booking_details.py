from loguru import logger

from voicetools.backends.provider import get_booking_backend


async def handle(params) -> None:
    args = params.arguments
    phone = args.get("phone_number", "")

    last_four = phone[-4:] if len(phone) >= 4 else phone
    logger.info("get_booking_details lookup for ...{}", last_four)

    backend = get_booking_backend()
    bookings = await backend.get_bookings_by_phone(phone)

    if not bookings:
        await params.result_callback(
            "I don't see any upcoming bookings for that number. "
            "Would you like to make a new booking?"
        )
        return

    lines = []
    for b in bookings:
        lines.append(
            f"Reference {b['ref']}: {b['service']} at {b['shop_name']} on {b['date']} at {b['time']}."
        )
    result = "Your upcoming bookings: " + " ".join(lines)
    await params.result_callback(result)
