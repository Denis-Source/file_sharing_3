from datetime import datetime
from urllib.parse import urlencode

import jwt
import pytest
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config import APP_NAME
from env import get_frontend_url, get_access_token_valid, get_refresh_token_valid, get_app_secret
from models.client import Client
from models.code import Code
from models.user import User
from services.authentication_serivce import AuthenticationService, JWT_ALGORITHM, TokenError, AuthenticationError, \
    TokenTypes
from services.user_service import UserService
from tests.conftest import generate_mock_password, get_mock_uri


def test_get_expiration_date_access():
    assert round(
        AuthenticationService.get_expiration_date(type_=TokenTypes.ACCESS).timestamp()
    ) == round(
        (datetime.utcnow() + get_access_token_valid()).timestamp())


def test_get_expiration_date_refresh():
    assert round(
        AuthenticationService.get_expiration_date(type_=TokenTypes.REFRESH).timestamp()
    ) == round(
        (datetime.utcnow() + get_refresh_token_valid()).timestamp())


def test_encode(mock_user: User):
    secret = "test_secret"

    token = AuthenticationService.generate_token(
        sub=mock_user.username,
        secret=secret
    )

    decoded_token = jwt.decode(
        token,
        secret,
        JWT_ALGORITHM
    )

    assert decoded_token.get("sub") == mock_user.username


def test_decode():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJhdXRoZW50aWNhdGlvbl9zZXJ" \
            "2aWNlIiwic3ViIjoxMjM0NTY3ODkwLCJpYXQ" \
            "iOjE3MTE2NzExMDAsImV4cCI6MjAwMDAwMDA" \
            "wMDB9" \
            ".ZI3oZpKDUSqWeYYnG7UXfNsdEc9W9Mq9M4x" \
            "DWQmyXyE"
    sub = 1234567890

    decoded_token = AuthenticationService.decode_token(token, secret)
    assert sub == decoded_token.get("sub")


def test_decode_invalid_signature():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJtZXRhZGF0YV9zZXJ2aWNlIiw" \
            "ic3ViIjoxMjM0NTY3ODkwLCJpYXQiOjE3MTE" \
            "2NzExMDAsImV4cCI6MjAwMDAwMDAwMDB9" \
            ".HXHmIoegomXWsgWOVGlh-QmIzu_Hld68LywdCD7AjCZ"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


def test_decode_invalid_exp():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJtZXRhZGF0YV9zZXJ2aWNlIiw" \
            "ic3ViIjoxMjM0NTY3ODkwLCJpYXQiOjE3MTE" \
            "2NzExMDAsImV4cCI6MH0" \
            ".VdcY5GZkIT2MLPPRZ_ECtTed9m_LbeA5x0Jit_WS5Os"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


def test_decode_missing_exp():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJtZXRhZGF0YV9zZXJ2aWNlIiw" \
            "ic3ViIjoxMjM0NTY3ODkwLCJpYXQiOjE3MTE" \
            "2NzExMDB9" \
            ".ZGcqMyiTpKY9A2yjQ4XTokiLXKDmKIQYZmqEp-Ce-8I"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


def test_decode_invalid_iss():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJzdWIiOjEyMzQ1Njc4OTAsImlhdCI6MTc" \
            "xMTY3MTEwMCwiZXhwIjoyMDAwMDAwMDAwMH0" \
            ".N3L45Fx4LrhqzdgO5TMYaDkmU-OKHYDUjUDU36wHXug"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


def test_decode_missing_iss():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJpc3MiOiJ3cm9uZ19pc3MiLCJzdWIiOjE" \
            "yMzQ1Njc4OTAsImlhdCI6MTcxMTY3MTEwMCw" \
            "iZXhwIjoyMDAwMDAwMDAwMH0" \
            ".1VF2pRozuF0p7bRN7aU5Ed4MPYOADnrkxbqCWM9_L9Y"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


def test_decode_invalid_format():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            "eyJzdWIiOjEyMzQ1Njc4OTAsIm5hbWUiOiJK" \
            "b2huIERvZSIsImlhdCI6MTUxNjIzOTAyMn0" \
            "xQ6rmPEgPsYj8n4XICbLSw_CuOQ6FqVqFNL" \
            "HTQbdQhY"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


def test_decode_no_sub():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            ".eyJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9" \
            ".nfxWdUayk54niAULlEOjvac-fUdltdWIYY1sg1Yd5Ts"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(token, secret)


async def test_create_oauth_token_success(test_session: AsyncSession, mock_user_with_password: tuple[User, str],
                                          mock_client: Client):
    secret = "test_secret"
    mock_user, password = mock_user_with_password
    auth_service = AuthenticationService(test_session)

    access_token, _ = await auth_service.create_password_pair(
        username=mock_user.username,
        password=password,
        client_id=mock_client.id,
        client_secret=mock_client.secret,
        secret=secret
    )
    decoded_token = jwt.decode(
        access_token,
        secret,
        JWT_ALGORITHM
    )
    assert decoded_token.get("sub") == mock_client.user.username


async def test_create_oauth_token_user_not_exist(test_session: AsyncSession, mock_client: Client):
    secret = "test_secret"
    username = "non_existent_username"
    password = generate_mock_password()

    auth_service = AuthenticationService(test_session)
    with pytest.raises(AuthenticationError):
        await auth_service.create_password_pair(
            username=username,
            password=password,
            client_id=mock_client.id,
            client_secret=mock_client.secret,
            secret=secret
        )


async def test_create_oauth_token_wrong_password(test_session: AsyncSession, mock_user: User, mock_client: Client):
    secret = "test_secret"
    wrong_password = generate_mock_password()
    auth_service = AuthenticationService(test_session)
    user_service = UserService(test_session)

    assert not await user_service.check_password(mock_user, wrong_password)
    with pytest.raises(AuthenticationError):
        await auth_service.create_password_pair(
            username=mock_user.username,
            password=wrong_password,
            client_id=mock_client.id,
            client_secret=mock_client.secret,
            secret=secret
        )


async def test_create_oauth_token_wrong_client_secret(test_session: AsyncSession,
                                                      mock_user_with_password: tuple[User, str],
                                                      mock_client: Client):
    secret = "test_secret"
    mock_user, password = mock_user_with_password
    auth_service = AuthenticationService(test_session)
    wrong_client_secret = "wrong_client_secret"

    assert wrong_client_secret != mock_client.secret
    with pytest.raises(AuthenticationError):
        await auth_service.create_password_pair(
            username=mock_user.username,
            password=password,
            client_id=mock_client.id,
            client_secret=wrong_client_secret,
            secret=secret
        )


async def test_create_oauth_token_wrong_user(test_session: AsyncSession,
                                             mock_user: User,
                                             another_mock_user_with_password: tuple[User, str],
                                             mock_client: Client):
    secret = "test_secret"
    another_mock_user, password = another_mock_user_with_password
    auth_service = AuthenticationService(test_session)
    wrong_client_secret = "wrong_client_secret"

    assert wrong_client_secret != mock_client.secret
    with pytest.raises(AuthenticationError):
        await auth_service.create_password_pair(
            username=another_mock_user.username,
            password=password,
            client_id=mock_client.id,
            client_secret=wrong_client_secret,
            secret=secret
        )


async def test_create_oauth_token_wrong_client_id(test_session: AsyncSession, mock_user_with_password: tuple[User, str],
                                                  mock_client: Client):
    secret = "test_secret"
    mock_user, password = mock_user_with_password
    auth_service = AuthenticationService(test_session)
    non_existent_id = int(1e9 + 42)

    with pytest.raises(AuthenticationError):
        await auth_service.create_password_pair(
            username=mock_user.username,
            password=password,
            client_id=non_existent_id,
            client_secret=mock_client.secret,
            secret=secret
        )


async def test_get_user_by_token_success(test_session: AsyncSession, mock_user: User):
    secret = "test_secret"
    auth_service = AuthenticationService(test_session)
    token = jwt.encode(
        {
            "sub": mock_user.username,
            "iss": APP_NAME,
            "type": TokenTypes.ACCESS,
            "iat": 1711671100,
            "exp": 20000000000
        },
        secret,
        JWT_ALGORITHM
    )

    user = await auth_service.get_user_by_token(
        token=token,
        secret=secret
    )
    assert user.id == mock_user.id


async def test_get_user_by_token_wrong_type(test_session: AsyncSession, mock_user: User):
    secret = "test_secret"
    auth_service = AuthenticationService(test_session)
    token = jwt.encode(
        {
            "sub": mock_user.username,
            "iss": APP_NAME,
            "type": TokenTypes.REFRESH,
            "iat": 1711671100,
            "exp": 20000000000
        },
        secret,
        JWT_ALGORITHM
    )
    with pytest.raises(AuthenticationError):
        user = await auth_service.get_user_by_token(
            token=token,
            secret=secret
        )


async def test_get_user_by_token_user_not_exist(test_session: AsyncSession, mock_client: Client):
    secret = "test_secret"
    auth_service = AuthenticationService(test_session)
    non_existent_username = "non_existent_username"
    token = jwt.encode(
        {
            "sub": non_existent_username,
            "iss": APP_NAME,
            "iat": 1711671100,
            "exp": 20000000000
        },
        secret,
        JWT_ALGORITHM
    )
    with pytest.raises(AuthenticationError):
        await auth_service.get_user_by_token(
            token=token,
            secret=secret
        )


async def test_authenticate_user_success(test_session: AsyncSession, mock_user_with_password: tuple[User, str]):
    mock_user, password = mock_user_with_password
    auth_service = AuthenticationService(test_session)
    assert mock_user == await auth_service.authenticate_user(
        username=mock_user.username,
        password=password
    )


async def test_authenticate_user_not_exist(test_session: AsyncSession):
    auth_service = AuthenticationService(test_session)
    non_existent_username = "not_existent_username"
    password = generate_mock_password()

    with pytest.raises(AuthenticationError):
        await auth_service.authenticate_user(
            username=non_existent_username,
            password=password
        )


async def test_authenticate_user_wrong_password(test_session: AsyncSession, mock_user: User):
    auth_service = AuthenticationService(test_session)
    user_service = UserService(test_session)
    password = generate_mock_password()

    assert not await user_service.check_password(
        instance=mock_user,
        plain_password=password
    )
    with pytest.raises(AuthenticationError):
        await auth_service.authenticate_user(
            username=mock_user.username,
            password=password
        )


async def test_get_auth_uri_success(mock_client: Client):
    redirect_uri = get_mock_uri()
    assert AuthenticationService.get_auth_uri(
        client_id=mock_client.id,
        redirect_uri=redirect_uri
    ) == f"{get_frontend_url()}" \
         f"/login/" \
         f"?{urlencode({'client_id': mock_client.id, 'redirect_uri': redirect_uri})}"


async def test_get_callback_uri_success(mock_code: Code):
    assert AuthenticationService.get_callback_uri(
        code=mock_code
    ) == f"{mock_code.redirect_uri}" \
         f"?{urlencode({'code': mock_code.value})}"


async def test_generate_code_success(test_session: AsyncSession, mock_client: Client):
    auth_service = AuthenticationService(test_session)

    code = await auth_service.generate_code(
        client_id=mock_client.id,
        redirect_uri=get_mock_uri()
    )

    assert await test_session.scalar(
        select(func.count()).where(
            Code.id == code.id)) == 1
    assert code.value

    await test_session.execute(
        delete(Code).where(Code.id == code.id)
    )


async def test_generate_code_non_existent_client(test_session: AsyncSession):
    auth_service = AuthenticationService(test_session)
    redirect_uri = get_mock_uri()
    non_existent_client_id = int(1e9 + 42)

    with pytest.raises(AuthenticationError):
        await auth_service.generate_code(
            client_id=non_existent_client_id,
            redirect_uri=redirect_uri
        )


async def test_check_code_success(test_session: AsyncSession, mock_client: Client, mock_code: Code):
    auth_service = AuthenticationService(test_session)
    code = await auth_service.check_code(
        client_id=mock_client.id,
        client_secret=mock_client.secret,
        redirect_uri=mock_code.redirect_uri,
        value=mock_code.value
    )

    assert code == mock_code


async def test_check_code_wrong_client_secret(test_session: AsyncSession, mock_client: Client, mock_code: Code):
    auth_service = AuthenticationService(test_session)
    wrong_secret = "wrong_secret"
    with pytest.raises(AuthenticationError):
        await auth_service.check_code(
            client_id=mock_client.id,
            client_secret=wrong_secret,
            redirect_uri=mock_code.redirect_uri,
            value=mock_code.value
        )


async def test_check_code_wrong_client_id(test_session: AsyncSession, mock_client: Client, mock_code: Code):
    auth_service = AuthenticationService(test_session)
    non_existent_client_id = int(1e9 + 42)
    with pytest.raises(AuthenticationError):
        await auth_service.check_code(
            client_id=non_existent_client_id,
            client_secret=mock_client.secret,
            redirect_uri=mock_code.redirect_uri,
            value=mock_code.value
        )


async def test_create_code_token_success(test_session: AsyncSession, mock_client: Client, mock_code: Code):
    auth_service = AuthenticationService(test_session)
    secret = "test_secret"

    access_token, refresh_token = await auth_service.create_code_pair(
        client_id=mock_client.id,
        client_secret=mock_client.secret,
        redirect_uri=mock_code.redirect_uri,
        value=mock_code.value,
        secret=secret
    )
    for token in [access_token, refresh_token]:
        decoded_token = jwt.decode(
            token,
            secret,
            JWT_ALGORITHM
        )
        assert decoded_token.get("sub") == mock_client.user.username


async def test_refresh_pair_success(test_session: AsyncSession, mock_client: Client, mock_token_pair: tuple[str, str]):
    _, mock_refresh_token = mock_token_pair
    auth_service = AuthenticationService(test_session)

    access_token, refresh_token = await auth_service.refresh_pair(
        refresh_token=mock_refresh_token,
        client_id=mock_client.id,
        client_secret=mock_client.secret
    )
    for token in [access_token, refresh_token]:
        decoded_token = jwt.decode(
            token,
            get_app_secret(),
            JWT_ALGORITHM
        )
        assert decoded_token.get("sub") == mock_client.user.username


async def test_refresh_pair_wrong_token_type(test_session: AsyncSession, mock_client: Client,
                                             mock_token_pair: tuple[str, str]):
    mock_access_token, _ = mock_token_pair
    auth_service = AuthenticationService(test_session)

    with pytest.raises(AuthenticationError):
        await auth_service.refresh_pair(
            refresh_token=mock_access_token,
            client_id=mock_client.id,
            client_secret=mock_client.secret
        )


async def test_refresh_pair_wrong_client_secret(test_session: AsyncSession, mock_client: Client,
                                                mock_token_pair: tuple[str, str]):
    wrong_client_secret = "secret"
    _, mock_refresh_token = mock_token_pair
    auth_service = AuthenticationService(test_session)

    with pytest.raises(AuthenticationError):
        await auth_service.refresh_pair(
            refresh_token=mock_refresh_token,
            client_id=mock_client.id,
            client_secret=wrong_client_secret
        )


async def test_refresh_pair_wrong_client_id(test_session: AsyncSession, mock_client: Client,
                                            mock_token_pair: tuple[str, str]):
    non_existent_client_id = int(1e9 + 42)
    _, mock_refresh_token = mock_token_pair
    auth_service = AuthenticationService(test_session)

    with pytest.raises(AuthenticationError):
        await auth_service.refresh_pair(
            refresh_token=mock_refresh_token,
            client_id=non_existent_client_id,
            client_secret=mock_client.secret
        )
