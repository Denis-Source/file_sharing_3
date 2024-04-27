import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def mock_http_client():
    return TestClient(app)
