from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.services.openai.llm import OpenAILLMService

from voicetools.tools import (
    create_booking,
    get_available_shops,
    get_booking_details,
    get_today_date,
    get_user_details,
)
from voicetools.tools import schemas

TOOL_REGISTRY = [
    ("get_available_shops", get_available_shops.handle),
    ("get_user_details", get_user_details.handle),
    ("create_booking", create_booking.handle),
    ("get_booking_details", get_booking_details.handle),
    ("get_today_date", get_today_date.handle),
]


def register_all_tools(llm: OpenAILLMService) -> ToolsSchema:
    for name, handler in TOOL_REGISTRY:
        llm.register_function(name, handler)
    return ToolsSchema(standard_tools=schemas.ALL_SCHEMAS)
