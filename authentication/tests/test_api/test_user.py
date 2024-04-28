from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.user.views import USER_URL_NAME, USER_URL_REGISTER
from models.client import Client
from models.user import User
from tests.conftest import generate_mock_name, generate_mock_plain_password


async def test_register_success(mock_http_client: AsyncClient, test_session: AsyncSession):
    username = generate_mock_name()
    password = generate_mock_plain_password()

    response = await mock_http_client.post(
        url=USER_URL_NAME + USER_URL_REGISTER,
        json={
            "username": username,
            "password": password
        }
    )
    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response.get("username") == username
    assert await test_session.scalar(
        select(func.count())
        .where(User.id == json_response.get("id"))) == 1


async def test_register_no_username(mock_http_client: AsyncClient, test_session: AsyncSession):
    password = generate_mock_plain_password()

    response = await mock_http_client.post(
        url=USER_URL_NAME + USER_URL_REGISTER,
        json={
            "password": password
        }
    )
    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert await test_session.scalar(
        select(func.count())
        .where(User.id == json_response.get("id"))) == 0


async def test_register_no_password(mock_http_client: AsyncClient, test_session: AsyncSession):
    username = generate_mock_name()

    response = await mock_http_client.post(
        url=USER_URL_NAME + USER_URL_REGISTER,
        json={
            "username": username
        }
    )
    json_response = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert await test_session.scalar(
        select(func.count())
        .where(User.id == json_response.get("id"))) == 0


async def test_register_already_exists(mock_http_client, test_session: AsyncSession, mock_user: User):
    password = generate_mock_plain_password()

    response = await mock_http_client.post(
        url=USER_URL_NAME + USER_URL_REGISTER,
        json={
            "username": mock_user.username,
            "password": password
        }
    )
    json_response = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert await test_session.scalar(
        select(func.count())
        .where(User.id == json_response.get("id"))) == 0
