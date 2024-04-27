import pytest
from httpx import AsyncClient

from app import app


@pytest.fixture
async def mock_http_client(event_loop):
    async with AsyncClient(app=app, base_url="https://testserver") as client:
        yield client
