from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

get_available_shops_schema = FunctionSchema(
    name="get_available_shops",
    description="Find nearby certified car wash and detailing shops",
    properties={
        "latitude": {"type": "number", "description": "User latitude"},
        "longitude": {"type": "number", "description": "User longitude"},
        "address": {"type": "string", "description": "User address or district"},
        "date": {"type": "string", "description": "Date to check availability (e.g. 'March 25')"},
        "service": {"type": "string", "description": "Service type to filter by"},
    },
    required=[],
)

get_user_details_schema = FunctionSchema(
    name="get_user_details",
    description="Look up customer details by phone number",
    properties={
        "phone_number": {"type": "string", "description": "Customer phone number"},
    },
    required=["phone_number"],
)

create_booking_schema = FunctionSchema(
    name="create_booking",
    description="Create a car wash or detailing booking",
    properties={
        "shop_name": {"type": "string", "description": "Selected shop name"},
        "service": {"type": "string", "description": "Service requested"},
        "date": {"type": "string", "description": "Booking date"},
        "time": {"type": "string", "description": "Booking time"},
        "customer_name": {"type": "string", "description": "Customer name"},
        "car_info": {"type": "string", "description": "Car make, model, plate"},
        "phone_number": {"type": "string", "description": "Customer phone number"},
    },
    required=["shop_name", "service", "date", "time"],
)

get_booking_details_schema = FunctionSchema(
    name="get_booking_details",
    description="Look up upcoming bookings by phone number",
    properties={
        "phone_number": {"type": "string", "description": "Customer phone number"},
    },
    required=["phone_number"],
)

get_today_date_schema = FunctionSchema(
    name="get_today_date",
    description="Get the current date and time in Vietnam timezone. Call this to validate booking dates.",
    properties={},
    required=[],
)

ALL_SCHEMAS = [
    get_available_shops_schema,
    get_user_details_schema,
    create_booking_schema,
    get_booking_details_schema,
    get_today_date_schema,
]
