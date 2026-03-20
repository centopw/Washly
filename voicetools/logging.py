import sys

from loguru import logger


def configure_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.add(sys.stderr, level=level, format="{time:HH:mm:ss.SSS} | {level:<7} | {message}")
