from fastapi import status
from fastapi.testclient import TestClient

from models.user import User
from tests.conftest import generate_mock_name, generate_mock_plain_password


def test_register_success(mock_http_client: TestClient):
    username = generate_mock_name()
    password = generate_mock_plain_password()

    response = mock_http_client.post(
        url="/auth/register/",
        json={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response.get("username") == username


def test_register_no_username(mock_http_client: TestClient):
    password = generate_mock_plain_password()

    response = mock_http_client.post(
        url="/auth/register/",
        json={
            "password": password
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_no_username(mock_http_client: TestClient):
    username = generate_mock_name()

    # TODO remove hardcode url
    response = mock_http_client.post(
        url="/auth/register/",
        json={
            "username": username
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_already_exists(mock_http_client: TestClient, mock_user: User):
    password = generate_mock_plain_password()

    response = mock_http_client.post(
        url="/auth/register/",
        json={
            "username": mock_user.username,
            "password": password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
