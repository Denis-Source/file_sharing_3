from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
from fastapi import HTTPException
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import authenticate
from api.auth.views import AUTH_URL_NAME, AuthRoutes
from app import app
from config import APP_NAME
from env import get_frontend_url, get_develop_mode, get_app_secret
from models.client import Client
from models.code import Code
from models.user import User
from services.authentication_serivce import AuthenticationService, TOKEN_SUB, TOKEN_ISS, TOKEN_IAT, TOKEN_EXP, \
    TOKEN_TYPE, TOKEN_SCOPES, TokenTypes, JWT_ALGORITHM
from tests.conftest import get_mock_uri


async def test_authenticate_success(
        test_session: AsyncSession,
        mock_token_pair: tuple[str, str],
        mock_user: User
):
    access_token, refresh_token = mock_token_pair
    auth_service = AuthenticationService(test_session)
    assert mock_user == await authenticate(
        token=access_token,
        auth_service=auth_service
    )


async def test_authenticate_no_required_scope(
        test_session: AsyncSession,
        mock_user: User
):
    decoded_token = {
        TOKEN_SUB: mock_user.username,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() + timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["wrong_scope"]}
    invalid_token = jwt.encode(
        decoded_token,
        get_app_secret(),
        algorithm=JWT_ALGORITHM
    )
    auth_service = AuthenticationService(test_session)
    with pytest.raises(HTTPException):
        await authenticate(
            token=invalid_token,
            auth_service=auth_service
        )


async def test_authenticate_invalid_token(
        test_session: AsyncSession,
        mock_user: User
):
    invalid_token = "invalid_token"
    auth_service = AuthenticationService(test_session)
    with pytest.raises(HTTPException):
        await authenticate(
            token=invalid_token,
            auth_service=auth_service
        )


async def test_code_auth_url_success(
        mock_http_client: AsyncClient,
        mock_client: Client):
    response = await mock_http_client.get(
        url=AUTH_URL_NAME + AuthRoutes.GET_AUTHORIZATION_URI,
        params={
            "client_id": mock_client.id,
            "redirect_uri": get_mock_uri()
        }
    )
    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert get_frontend_url() in json_response.get("redirect_uri")


async def test_code_auth_url_no_client_id(
        mock_http_client: AsyncClient):
    response = await mock_http_client.get(
        url=AUTH_URL_NAME + AuthRoutes.GET_AUTHORIZATION_URI,
        params={
            "redirect_uri": get_mock_uri()
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_code_auth_url_no_redirect_uri(
        mock_http_client: AsyncClient,
        mock_client: Client):
    response = await mock_http_client.get(
        url=AUTH_URL_NAME + AuthRoutes.GET_AUTHORIZATION_URI,
        params={
            "client_id": mock_client.id,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_callback_code_success(
        mock_http_client: AsyncClient,
        test_session: AsyncSession,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]):
    mock_user, password = mock_user_with_password
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.CALLBACK_CODE,
        params={
            "client_id": mock_client.id,
            "redirect_uri": get_mock_uri()
        },
        json={
            "username": mock_user.username,
            "password": password
        }
    )
    response_json = response.json()
    parsed = urlparse(response_json.get("redirect_uri"))
    code_value = parse_qs(parsed.query).get("code")[0]

    assert response.status_code == status.HTTP_200_OK
    assert await test_session.scalar(
        select(func.count())
        .where(Code.value == code_value)) == 1


async def test_callback_code_no_client_id(
        mock_http_client: AsyncClient,
        test_session: AsyncSession,
        mock_user_with_password: tuple[User, str]):
    mock_user, password = mock_user_with_password
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.CALLBACK_CODE,
        params={
            "redirect_uri": get_mock_uri()
        },
        json={
            "username": mock_user.username,
            "password": password
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_callback_code_no_redirect_uri(
        mock_http_client: AsyncClient,
        test_session: AsyncSession,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]):
    mock_user, password = mock_user_with_password
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.CALLBACK_CODE,
        params={
            "client_id": mock_client.id,
        },
        json={
            "username": mock_user.username,
            "password": password
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_callback_code_no_username(
        mock_http_client: AsyncClient,
        test_session: AsyncSession,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]):
    _, password = mock_user_with_password
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.CALLBACK_CODE,
        params={
            "client_id": mock_client.id,
            "redirect_uri": get_mock_uri()
        },
        json={
            "password": password
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_callback_code_no_password(
        mock_http_client: AsyncClient,
        test_session: AsyncSession,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]):
    mock_user, _ = mock_user_with_password
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.CALLBACK_CODE,
        params={
            "client_id": mock_client.id,
            "redirect_uri": get_mock_uri()
        },
        json={
            "username": mock_user.username,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_code_success(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_code: Code
):
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.TOKEN_CODE,
        json={
            "code": mock_code.value,
            "client_id": mock_client.id,
            "client_secret": mock_client.secret,
            "redirect_uri": mock_code.redirect_uri
        }
    )
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("access_token")
    assert response_json.get("refresh_token")


async def test_token_code_no_code(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_code: Code
):
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.TOKEN_CODE,
        json={
            "client_id": mock_client.id,
            "client_secret": mock_client.secret,
            "redirect_uri": mock_code.redirect_uri
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_code_no_client_id(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_code: Code
):
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.TOKEN_CODE,
        json={
            "code": mock_code.value,
            "client_secret": mock_client.secret,
            "redirect_uri": mock_code.redirect_uri
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_code_no_client_secret(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_code: Code
):
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.TOKEN_CODE,
        json={
            "code": mock_code.value,
            "client_id": mock_client.id,
            "redirect_uri": mock_code.redirect_uri
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_code_no_redirect_uri(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_code: Code
):
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.TOKEN_CODE,
        json={
            "code": mock_code.value,
            "client_id": mock_client.id,
            "client_secret": mock_client.secret,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_password_success(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]
):
    with fastapi_dep(app).override({get_develop_mode: lambda: True}):
        mock_user, password = mock_user_with_password
        response = await mock_http_client.post(
            url=AUTH_URL_NAME + AuthRoutes.TOKEN_PASSWORD,
            data={
                "username": mock_user.username,
                "password": password,
                "client_id": mock_client.id,
                "client_secret": mock_client.secret
            }
        )
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("access_token")
    assert response_json.get("refresh_token") is None


async def test_token_password_development_mode_off(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]
):
    mock_user, password = mock_user_with_password
    with fastapi_dep(app).override({get_develop_mode: lambda: False}):
        response = await mock_http_client.post(
            url=AUTH_URL_NAME + AuthRoutes.TOKEN_PASSWORD,
            data={
                "username": mock_user.username,
                "password": password,
                "client_id": mock_client.id,
                "client_secret": mock_client.secret
            }
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_token_password_no_username(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]
):
    mock_user, password = mock_user_with_password
    with fastapi_dep(app).override({get_develop_mode: lambda: True}):
        response = await mock_http_client.post(
            url=AUTH_URL_NAME + AuthRoutes.TOKEN_PASSWORD,
            data={
                "password": password,
                "client_id": mock_client.id,
                "client_secret": mock_client.secret
            }
        )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_password_no_password(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]
):
    mock_user, password = mock_user_with_password
    with fastapi_dep(app).override({get_develop_mode: lambda: True}):
        response = await mock_http_client.post(
            url=AUTH_URL_NAME + AuthRoutes.TOKEN_PASSWORD,
            data={
                "username": mock_user.username,
                "client_id": mock_client.id,
                "client_secret": mock_client.secret
            }
        )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_password_no_client_id(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]
):
    mock_user, password = mock_user_with_password
    with fastapi_dep(app).override({get_develop_mode: lambda: True}):
        response = await mock_http_client.post(
            url=AUTH_URL_NAME + AuthRoutes.TOKEN_PASSWORD,
            data={
                "username": mock_user.username,
                "password": password,
                "client_secret": mock_client.secret
            }
        )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_token_password_no_client_secret(
        fastapi_dep,
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_user_with_password: tuple[User, str]
):
    mock_user, password = mock_user_with_password
    with fastapi_dep(app).override({get_develop_mode: lambda: True}):
        response = await mock_http_client.post(
            url=AUTH_URL_NAME + AuthRoutes.TOKEN_PASSWORD,
            data={
                "username": mock_user.username,
                "password": password,
                "client_id": mock_client.id,
            }
        )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_refresh_success(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_token_pair: tuple[str, str]
):
    _, refresh_token = mock_token_pair
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.REFRESH,
        json={
            "refresh_token": refresh_token,
            "client_id": mock_client.id,
            "client_secret": mock_client.secret
        }
    )
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json.get("access_token")
    assert response_json.get("refresh_token")


async def test_refresh_no_refresh_token(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_token_pair: tuple[str, str]
):
    _, refresh_token = mock_token_pair
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.REFRESH,
        json={
            "client_id": mock_client.id,
            "client_secret": mock_client.secret
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_refresh_no_client_id(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_token_pair: tuple[str, str]
):
    _, refresh_token = mock_token_pair
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.REFRESH,
        json={
            "refresh_token": refresh_token,
            "client_secret": mock_client.secret
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_refresh_no_client_secret(
        mock_http_client: AsyncClient,
        mock_client: Client,
        mock_token_pair: tuple[str, str]
):
    _, refresh_token = mock_token_pair
    response = await mock_http_client.post(
        url=AUTH_URL_NAME + AuthRoutes.REFRESH,
        json={
            "refresh_token": refresh_token,
            "client_id": mock_client.id,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_verify_success(
        mock_http_client: AsyncClient,
        mock_auth_header: dict
):
    response = await mock_http_client.post(
        AUTH_URL_NAME + AuthRoutes.VERIFY,
        headers=mock_auth_header
    )

    assert response.status_code == status.HTTP_200_OK


async def test_verify_wrong_token_type(
        mock_http_client: AsyncClient,
        mock_token_pair: tuple[str, str]
):
    _, refresh_token = mock_token_pair
    response = await mock_http_client.post(
        AUTH_URL_NAME + AuthRoutes.VERIFY,
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_verify_wrong_token(
        mock_http_client: AsyncClient
):
    response = await mock_http_client.post(
        AUTH_URL_NAME + AuthRoutes.VERIFY,
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_verify_no_token(
        mock_http_client: AsyncClient
):
    response = await mock_http_client.post(
        AUTH_URL_NAME + AuthRoutes.VERIFY
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
