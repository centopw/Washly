from loguru import logger

from voicetools.backends.provider import get_shop_backend


async def handle(params) -> None:
    args = params.arguments
    latitude = args.get("latitude")
    longitude = args.get("longitude")
    address = args.get("address")
    date = args.get("date")
    service = args.get("service")

    backend = get_shop_backend()
    shops = await backend.find_nearby_shops(
        latitude=latitude,
        longitude=longitude,
        address=address,
        date=date,
        service=service,
    )

    if not shops:
        await params.result_callback("No certified shops found in your area.")
        return

    lines = []
    for shop in shops:
        line = (
            f"{shop['name']} in {shop['location']}: rated {shop['rating']} stars, "
            f"specializing in {shop['specialty']}, open {shop['hours']}."
        )
        if "available_slots" in shop:
            if shop.get("fully_booked"):
                line += " Fully booked for this date."
            else:
                slots = ", ".join(shop["available_slots"])
                line += f" Available slots: {slots}."
        lines.append(line)

    result = " ".join(lines)
    logger.info("get_available_shops returned {} shops", len(shops))
    await params.result_callback(result)
