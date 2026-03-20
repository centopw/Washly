import pytest

from voicetools.tools import get_user_details


@pytest.mark.asyncio
async def test_handle_known_phone_returns_user(mock_params):
    mock_params.arguments = {"phone_number": "+84901234567"}
    await get_user_details.handle(mock_params)
    result = mock_params.result_callback.call_args[0][0]
    assert "Nguyen Van An" in result
    assert "VIP" in result


@pytest.mark.asyncio
async def test_handle_unknown_phone_returns_not_found(mock_params):
    mock_params.arguments = {"phone_number": "+84999999999"}
    await get_user_details.handle(mock_params)
    result = mock_params.result_callback.call_args[0][0]
    assert "No customer found" in result
