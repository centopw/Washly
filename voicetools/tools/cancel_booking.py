from loguru import logger

from voicetools.backends.provider import get_booking_backend


async def handle(params) -> None:
    args = params.arguments
    ref = args.get("booking_ref", "")

    backend = get_booking_backend()
    result = await backend.cancel_booking(ref)

    if result.get("error"):
        await params.result_callback(result["error"])
        return

    logger.info("Booking cancelled | ref={}", ref)
    await params.result_callback(
        f"Booking {ref} has been successfully cancelled."
    )
