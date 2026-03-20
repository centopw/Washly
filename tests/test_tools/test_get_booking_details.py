import pytest

from voicetools.backends.bookings import MockBookingBackend
from voicetools.tools import get_booking_details


@pytest.mark.asyncio
async def test_handle_no_bookings_returns_empty_message(mock_params):
    mock_params.arguments = {"phone_number": "+84999999999"}
    await get_booking_details.handle(mock_params)
    result = mock_params.result_callback.call_args[0][0]
    assert "upcoming bookings" in result.lower()


@pytest.mark.asyncio
async def test_handle_returns_booking_after_creation():
    backend = MockBookingBackend()
    await backend.create_booking(
        shop_name="Prestige Auto Care",
        service="PPF",
        date="April 1",
        time="9am",
        phone="+84911111111",
    )
    bookings = await backend.get_bookings_by_phone("+84911111111")
    assert len(bookings) == 1
    assert bookings[0]["shop_name"] == "Prestige Auto Care"
    assert bookings[0]["ref"].startswith("VAL-")
    assert len(bookings[0]["ref"]) == 12  # "VAL-" + 8 hex chars
