from loguru import logger

from voicetools.utils import get_current_date


async def handle(params) -> None:
    date_info = get_current_date()
    logger.info("get_today_date called, returning {}", date_info["iso_date"])
    await params.result_callback(date_info)
