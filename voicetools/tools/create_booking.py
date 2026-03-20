from datetime import datetime

from loguru import logger

from voicetools.backends.provider import get_booking_backend
from voicetools.utils import TIMEZONE


async def handle(params) -> None:
    args = params.arguments
    shop_name = args.get("shop_name", "")
    service = args.get("service", "")
    date = args.get("date", "")
    time = args.get("time", "")
    customer_name = args.get("customer_name", "")
    car_info = args.get("car_info", "")
    phone = args.get("phone_number", "")

    backend = get_booking_backend()
    booking = await backend.create_booking(
        shop_name=shop_name,
        service=service,
        date=date,
        time=time,
        customer_name=customer_name,
        car_info=car_info,
        phone=phone,
    )

    if booking.get("conflict"):
        await params.result_callback(booking["error"])
        return

    ref = booking["ref"]
    logger.info(
        "Booking created | ref={} shop={} service={} date={} time={} customer={}",
        ref, shop_name, service, date, time, customer_name or "not provided",
    )
    result = (
        f"Booking confirmed. Your reference is {ref}. "
        f"We have you booked at {shop_name} for {service} on {date} at {time}."
    )
    await params.result_callback(result)
