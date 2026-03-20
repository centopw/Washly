import pytest

from voicetools.tools import create_booking


@pytest.mark.asyncio
async def test_handle_creates_booking_with_ref(mock_params):
    mock_params.arguments = {
        "shop_name": "Elite Detail Studio",
        "service": "Full Detail",
        "date": "March 25",
        "time": "10am",
        "customer_name": "Test Customer",
    }
    await create_booking.handle(mock_params)
    result = mock_params.result_callback.call_args[0][0]
    assert "VAL-" in result
    assert "Elite Detail Studio" in result
    assert "Full Detail" in result


@pytest.mark.asyncio
async def test_handle_returns_confirmation_message(mock_params):
    mock_params.arguments = {
        "shop_name": "Diamond Wash",
        "service": "Express Wash",
        "date": "March 26",
        "time": "2pm",
    }
    await create_booking.handle(mock_params)
    result = mock_params.result_callback.call_args[0][0]
    assert "Booking confirmed" in result
