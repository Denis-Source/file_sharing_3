import asyncio
import random
from string import ascii_lowercase, digits

import pytest
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from config import get_test_database_url, ADAPTERS
from migrations.operations import migrate_head
from models.client import Client
from models.user import User
from services.client_service import ClientService
from services.user_service import UserService


def generate_mock_name(length: int = 10):
    return "".join(random.choices(ascii_lowercase + digits, k=length))


def generate_mock_email(domain="mockemail.com", length: int = 10):
    return f"{generate_mock_name(length)}@{domain}"


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
        email=generate_mock_email(),
        plain_password=generate_mock_plain_password()
    )

    user_id = user.id
    yield user

    await service.delete(user_id)


@pytest.fixture
async def mock_client(test_session: AsyncSession, mock_user: User) -> Client:
    service = ClientService(test_session)
    client = await service.create(
        user=mock_user
    )

    client_id = client.id
    yield client

    await service.delete(client_id)
