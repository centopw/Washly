from loguru import logger

from voicetools.backends.provider import get_booking_backend


async def handle(params) -> None:
    args = params.arguments
    ref = args.get("booking_ref", "")
    new_date = args.get("new_date", "")
    new_time = args.get("new_time", "")

    backend = get_booking_backend()

    old = await backend.get_booking_by_ref(ref)
    if not old:
        await params.result_callback(f"Booking {ref} not found.")
        return

    cancel_result = await backend.cancel_booking(ref)
    if cancel_result.get("error"):
        await params.result_callback(cancel_result["error"])
        return

    new_booking = await backend.create_booking(
        shop_name=old["shop_name"],
        service=old["service"],
        date=new_date,
        time=new_time,
        customer_name=old.get("customer_name", ""),
        car_info=old.get("car_info", ""),
        phone=old.get("phone", ""),
    )

    if new_booking.get("conflict"):
        await params.result_callback(new_booking["error"])
        return

    new_ref = new_booking["ref"]
    logger.info("Booking rescheduled | old_ref={} new_ref={} date={} time={}", ref, new_ref, new_date, new_time)
    await params.result_callback(
        f"Booking rescheduled. Your new reference is {new_ref}. "
        f"You are now booked at {old['shop_name']} for {old['service']} on {new_date} at {new_time}."
    )
