from fastapi import status
from httpx import AsyncClient

from api.client.views import CLIENT_URL_NAME, ClientRoutes
from models.scope import Scope
from models.user import User
from tests.conftest import generate_mock_name


async def test_create_success(
        mock_http_client: AsyncClient,
        mock_user: User
):
    response = await mock_http_client.post(
        url=CLIENT_URL_NAME + ClientRoutes.CREATE,
        json={
            "username": mock_user.username,
            "client_name": generate_mock_name(),
            "scopes": [Scope.Types.UNRESTRICTED]
        }
    )
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("id")
    assert response_json.get("name")
    assert response_json.get("secret")


async def test_create_no_username(
        mock_http_client: AsyncClient
):
    response = await mock_http_client.post(
        url=CLIENT_URL_NAME + ClientRoutes.CREATE,
        json={
            "client_name": generate_mock_name(),
            "scopes": [Scope.Types.UNRESTRICTED]
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_no_client_name(
        mock_http_client: AsyncClient,
        mock_user: User
):
    response = await mock_http_client.post(
        url=CLIENT_URL_NAME + ClientRoutes.CREATE,
        json={
            "username": mock_user.username,
            "scopes": [Scope.Types.UNRESTRICTED]
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_not_existent_username(
        mock_http_client: AsyncClient
):
    response = await mock_http_client.post(
        url=CLIENT_URL_NAME + ClientRoutes.CREATE,
        json={
            "username": "non_existent_username",
            "client_name": generate_mock_name(),
            "scopes": [Scope.Types.UNRESTRICTED]
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_create_no_scopes(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_user: User
):
    response = await mock_http_client.post(
        url=CLIENT_URL_NAME + ClientRoutes.CREATE,
        json={
            "username": mock_user.username,
            "client_name": generate_mock_name()
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
