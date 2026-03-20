from loguru import logger

from voicetools.backends.provider import get_user_backend


async def handle(params) -> None:
    args = params.arguments
    phone = args.get("phone_number", "")

    last_four = phone[-4:] if len(phone) >= 4 else phone
    logger.info("get_user_details lookup for ...{}", last_four)

    backend = get_user_backend()
    user = await backend.get_user_by_phone(phone)

    if not user:
        await params.result_callback(
            "No customer found with that phone number. "
            "Would you like to proceed as a new customer?"
        )
        return

    result = (
        f"Found customer {user['name']}, {user['tier']} member, "
        f"driving a {user['car_make']} {user['car_model']} with plate {user['car_plate']}."
    )
    await params.result_callback(result)
