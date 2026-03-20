import pytest
from unittest.mock import MagicMock, AsyncMock

from voicetools.tools import get_available_shops


@pytest.mark.asyncio
async def test_handle_returns_shops(mock_params):
    mock_params.arguments = {"address": "District 2"}
    await get_available_shops.handle(mock_params)
    mock_params.result_callback.assert_called_once()
    result = mock_params.result_callback.call_args[0][0]
    assert "Elite Detail Studio" in result


@pytest.mark.asyncio
async def test_handle_works_with_coords(mock_params):
    mock_params.arguments = {"latitude": 10.79, "longitude": 106.74}
    await get_available_shops.handle(mock_params)
    mock_params.result_callback.assert_called_once()
    result = mock_params.result_callback.call_args[0][0]
    assert "stars" in result
