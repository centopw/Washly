import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

SLOT_TIMES = ["8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm"]


def generate_booking_ref() -> str:
    return f"VAL-{uuid.uuid4().hex[:8].upper()}"


def normalize_phone(phone: str) -> str:
    return phone.replace(" ", "").replace("-", "")


def get_current_date() -> dict:
    now = datetime.now(TIMEZONE)
    return {
        "today": now.strftime("%A, %B %d, %Y"),
        "iso_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%-I:%M %p"),
        "timezone": "Asia/Ho_Chi_Minh",
    }
