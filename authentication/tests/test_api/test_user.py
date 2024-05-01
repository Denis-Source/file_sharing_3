from fastapi import status
from httpx import AsyncClient

from api.user.views import USER_URL_NAME, UserRoutes
from models.user import User
from tests.conftest import generate_mock_name, generate_mock_plain_password


async def test_register_success(
        mock_http_client: AsyncClient
):
    username = generate_mock_name()
    password = generate_mock_plain_password()

    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.REGISTER,
        json={
            "username": username,
            "password": password
        }
    )
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("id")
    assert response_json.get("username")
    assert response_json.get("created_at")


async def test_register_no_username(
        mock_http_client: AsyncClient
):
    password = generate_mock_plain_password()

    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.REGISTER,
        json={
            "password": password
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_register_no_password(
        mock_http_client: AsyncClient
):
    username = generate_mock_name()

    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.REGISTER,
        json={
            "username": username
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_register_already_exists(
        mock_http_client: AsyncClient,
        mock_user: User
):
    password = generate_mock_plain_password()

    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.REGISTER,
        json={
            "username": mock_user.username,
            "password": password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_profile_success(
        mock_http_client: AsyncClient,
        mock_user: User,
        mock_auth_header: dict
):
    response = await mock_http_client.get(
        url=USER_URL_NAME + UserRoutes.PROFILE,
        headers=mock_auth_header
    )
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("id")
    assert response_json.get("username")
    assert response_json.get("created_at")


async def test_profile_unauthorized(
        mock_http_client: AsyncClient,
        mock_user: User,
):
    response = await mock_http_client.get(
        url=USER_URL_NAME + UserRoutes.PROFILE
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_set_password_success(
        mock_http_client: AsyncClient,
        mock_user: User,
        mock_auth_header: dict
):
    password = generate_mock_plain_password()
    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.SET_PASSWORD,
        json={
            "new_password": password
        },
        headers=mock_auth_header
    )
    assert response.status_code == status.HTTP_200_OK


async def test_set_password_no_password(
        mock_http_client: AsyncClient,
        mock_user: User,
        mock_auth_header: dict
):
    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.SET_PASSWORD,
        json={},
        headers=mock_auth_header
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_set_password_unauthorized(
        mock_http_client: AsyncClient,
        mock_user: User
):
    password = generate_mock_plain_password()
    response = await mock_http_client.post(
        url=USER_URL_NAME + UserRoutes.SET_PASSWORD,
        json={
            "new_password": password
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
