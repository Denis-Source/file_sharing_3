import asyncio
import os
import random
from datetime import datetime, timedelta
from string import ascii_lowercase, digits

import pytest
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from config import get_test_database_url, ADAPTERS
from env import get_authentication_code_valid_minutes, set_env_key
from migrations.operations import migrate_head
from models.client import Client
from models.code import Code
from models.user import User
from services.authentication_serivce import AuthenticationService
from services.client_service import ClientService
from services.code_service import CodeService
from services.user_service import UserService


def generate_mock_name(length: int = 10):
    return "".join(random.choices(ascii_lowercase + digits, k=length))


def generate_mock_plain_password(length: int = 10) -> str:
    return "".join(random.choices(ascii_lowercase + digits, k=length))


def generate_mock_password() -> str:
    return "test$1$plain_password$salt"


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_engine() -> AsyncEngine:
    migrate_head(get_test_database_url(ADAPTERS.SYNC))

    engine = create_async_engine(
        get_test_database_url(ADAPTERS.ASYNC),
        poolclass=AsyncAdaptedQueuePool,
    )

    yield engine

    engine.dispose()


@pytest.fixture
async def test_session(event_loop, test_db_engine: AsyncEngine) -> AsyncSession:
    async with AsyncSession(
            test_db_engine,
            expire_on_commit=False) as session:
        yield session


@pytest.fixture
async def mock_user(test_session: AsyncSession) -> User:
    service = UserService(test_session)
    user = await service.create(
        username=f"user_{generate_mock_name()}",
        plain_password=generate_mock_plain_password()
    )

    user_id = user.id
    yield user

    await service.delete(user_id)


@pytest.fixture
async def another_mock_user(test_session: AsyncSession) -> User:
    service = UserService(test_session)
    user = await service.create(
        username=f"user_{generate_mock_name()}",
        plain_password=generate_mock_plain_password()
    )

    user_id = user.id
    yield user

    await service.delete(user_id)


@pytest.fixture
async def mock_user_with_password(test_session: AsyncSession, mock_user: User) -> tuple[User, str]:
    service = UserService(test_session)
    plain_password = generate_mock_plain_password()
    await service.set_password(
        instance=mock_user,
        plain_password=plain_password
    )
    return mock_user, plain_password


@pytest.fixture
async def another_mock_user_with_password(test_session: AsyncSession, another_mock_user: User) -> tuple[User, str]:
    service = UserService(test_session)
    plain_password = generate_mock_plain_password()
    await service.set_password(
        instance=another_mock_user,
        plain_password=plain_password
    )
    return another_mock_user, plain_password


@pytest.fixture
async def mock_client(test_session: AsyncSession, mock_user: User) -> Client:
    service = ClientService(test_session)
    client = await service.create(
        name=f"client_{generate_mock_name()}",
        user=mock_user
    )

    client_id = client.id
    yield client

    await service.delete(client_id)


def get_mock_uri():
    return "https://example.com/callback/"


@pytest.fixture
async def mock_code(test_session: AsyncSession, mock_client: Client) -> Code:
    service = CodeService(test_session)
    code = await service.create(
        client=mock_client,
        redirect_uri=get_mock_uri(),
        valid_until=datetime.now() + timedelta(get_authentication_code_valid_minutes())
    )

    code_id = code.id
    yield code

    await service.delete(code_id)


@pytest.fixture
async def mock_token_pair(test_session: AsyncSession, mock_user_with_password: User, mock_client: Client):
    auth_service = AuthenticationService(test_session)
    mock_user, password = mock_user_with_password
    return await auth_service.create_password_pair(
        username=mock_user.username,
        password=password,
        client_id=mock_client.id,
        client_secret=mock_client.secret
    )


@pytest.fixture
async def mock_auth_header(mock_token_pair: tuple[str, str]):
    access_token, _ = mock_token_pair
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def develop_mode_on():
    key = "APP_DEVELOP_MODE"
    old_value = os.getenv(key)
    os.environ[key] = "True"
    yield

    set_env_key(key, old_value)


@pytest.fixture
def develop_mode_off():
    key = "APP_DEVELOP_MODE"
    old_value = os.getenv(key)
    os.environ[key] = "False"
    yield

    set_env_key(key, old_value)
