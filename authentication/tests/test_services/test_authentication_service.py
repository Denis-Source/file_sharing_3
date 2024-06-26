from datetime import datetime, timedelta
from urllib.parse import urlencode

import jwt
import pytest
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config import APP_NAME
from env import get_frontend_url, get_access_token_valid, get_refresh_token_valid, get_app_secret
from models.client import Client
from models.code import Code
from models.scope import Scope
from models.user import User
from services.authentication_serivce import AuthenticationService, JWT_ALGORITHM, TokenError, AuthenticationError, \
    TokenTypes, TOKEN_SCOPES, TOKEN_SUB, TOKEN_ISS, TOKEN_IAT, TOKEN_EXP, TOKEN_TYPE
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

    assert decoded_token.get(TOKEN_SUB) == mock_user.username


def test_decode_success():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() + timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )

    assert decoded_token == AuthenticationService.decode_token(
        token=token,
        secret=secret
    )


def test_decode_success_required_type():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() + timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    decoded_token = AuthenticationService.decode_token(
        token=token,
        required_type=TokenTypes.ACCESS,
        secret=secret
    )
    assert decoded_token == AuthenticationService.decode_token(
        token=token,
        secret=secret
    )


def test_decode_invalid_signature():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() + timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            required_type=TokenTypes.ACCESS,
            secret="different_secret"
        )


def test_decode_invalid_exp():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() - timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            required_type=TokenTypes.ACCESS,
            secret=secret
        )


def test_decode_not_required_type():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() - timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.REFRESH,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            required_type=TokenTypes.ACCESS,
            secret=secret
        )


def test_decode_missing_exp():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            required_type=TokenTypes.ACCESS,
            secret=secret
        )


def test_decode_invalid_iss():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_ISS: "different_issuer",
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_TYPE: TokenTypes.REFRESH,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            required_type=TokenTypes.ACCESS,
            secret=secret
        )


def test_decode_missing_iss():
    secret = "test_secret"
    decoded_token = {
        TOKEN_SUB: 1234567890,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() + timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            secret=secret
        )


def test_decode_invalid_format():
    secret = "test_secret"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" \
            "eyJzdWIiOjEyMzQ1Njc4OTAsIm5hbWUiOiJK" \
            "b2huIERvZSIsImlhdCI6MTUxNjIzOTAyMn0" \
            "xQ6rmPEgPsYj8n4XICbLSw_CuOQ6FqVqFNL" \
            "HTQbdQhY"

    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            secret=secret
        )


def test_decode_no_sub():
    secret = "test_secret"
    decoded_token = {
        TOKEN_ISS: APP_NAME,
        TOKEN_IAT: datetime.utcnow().timestamp(),
        TOKEN_EXP: (datetime.utcnow() + timedelta(days=10)).timestamp(),
        TOKEN_TYPE: TokenTypes.ACCESS,
        TOKEN_SCOPES: ["test_scope"]}

    token = jwt.encode(
        decoded_token,
        secret,
        algorithm=JWT_ALGORITHM
    )
    with pytest.raises(TokenError):
        AuthenticationService.decode_token(
            token=token,
            secret=secret
        )


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
    assert decoded_token.get(TOKEN_SUB) == mock_client.user.username


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
            TOKEN_SUB: mock_user.username,
            TOKEN_ISS: APP_NAME,
            TOKEN_TYPE: TokenTypes.ACCESS,
            TOKEN_IAT: 1711671100,
            TOKEN_EXP: 20000000000,
            TOKEN_SCOPES: []
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
            TOKEN_SUB: mock_user.username,
            TOKEN_ISS: APP_NAME,
            TOKEN_TYPE: TokenTypes.REFRESH,
            TOKEN_IAT: 1711671100,
            TOKEN_EXP: 20000000000,
            TOKEN_SCOPES: []
        },
        secret,
        JWT_ALGORITHM
    )
    with pytest.raises(AuthenticationError):
        await auth_service.get_user_by_token(
            token=token,
            secret=secret
        )


async def test_get_user_by_token_user_not_exist(test_session: AsyncSession, mock_client: Client):
    secret = "test_secret"
    auth_service = AuthenticationService(test_session)
    non_existent_username = "non_existent_username"
    token = jwt.encode(
        {
            TOKEN_SUB: non_existent_username,
            TOKEN_ISS: APP_NAME,
            TOKEN_TYPE: TokenTypes.REFRESH,
            TOKEN_IAT: 1711671100,
            TOKEN_EXP: 20000000000,
            TOKEN_SCOPES: []
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
    assert not mock_code.is_used


async def test_check_code_success_invalidated(test_session: AsyncSession, mock_client: Client, mock_code: Code):
    auth_service = AuthenticationService(test_session)
    code = await auth_service.check_code(
        client_id=mock_client.id,
        client_secret=mock_client.secret,
        redirect_uri=mock_code.redirect_uri,
        value=mock_code.value,
        invalidate=True
    )

    assert code == mock_code
    assert code.is_used


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
    decoded_access_token = jwt.decode(
        access_token,
        secret,
        JWT_ALGORITHM
    )
    decoded_refresh_token = jwt.decode(
        refresh_token,
        secret,
        JWT_ALGORITHM
    )
    assert decoded_access_token.get(TOKEN_SUB) == decoded_refresh_token.get(TOKEN_SUB) == mock_client.user.username
    assert set(decoded_access_token.get(TOKEN_SCOPES)) == set([scope.type for scope in mock_client.scopes])
    assert mock_code.is_used


async def test_refresh_pair_success(test_session: AsyncSession, mock_client: Client, mock_token_pair: tuple[str, str]):
    _, mock_refresh_token = mock_token_pair
    auth_service = AuthenticationService(test_session)

    access_token, refresh_token = await auth_service.refresh_pair(
        refresh_token=mock_refresh_token,
        client_id=mock_client.id,
        client_secret=mock_client.secret
    )
    decoded_access_token = jwt.decode(
        access_token,
        get_app_secret(),
        JWT_ALGORITHM
    )
    decoded_refresh_token = jwt.decode(
        refresh_token,
        get_app_secret(),
        JWT_ALGORITHM
    )
    assert decoded_access_token.get(TOKEN_SUB) == decoded_refresh_token.get(TOKEN_SUB) == mock_client.user.username
    assert set(decoded_access_token.get(TOKEN_SCOPES)) == set([scope.type for scope in mock_client.scopes])


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


async def test_get_scopes_success(test_session: AsyncSession, mock_token_pair: tuple[str, str]):
    access_token, _ = mock_token_pair
    auth_service = AuthenticationService(test_session)
    scopes = auth_service.get_scopes(access_token)
    assert set(scopes) == {Scope.Types.UNRESTRICTED.value}
