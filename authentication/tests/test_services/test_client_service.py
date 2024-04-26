from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.client import Client
from models.user import User
from services.base import UniquenessError
from services.client_service import ClientService
from tests.conftest import generate_mock_name


async def test_create(test_session: AsyncSession, mock_user: User):
    service = ClientService(test_session)
    name = f"client_{generate_mock_name()}"

    client = await service.create(
        name=name,
        user=mock_user
    )
    assert client in await test_session.scalars(select(Client))
    assert await test_session.scalar(
        select(func.count())
        .where(Client.id == client.id)) == 1

    await test_session.execute(delete(Client).where(Client.id == client.id))
    await test_session.commit()


async def test_name_uniqueness(test_session: AsyncSession, mock_user: User, mock_client: Client):
    service = ClientService(test_session)

    with pytest.raises(UniquenessError):
        await service.create(
            name=mock_client.name,
            user=mock_user
        )


async def test_delete(test_session: AsyncSession, mock_client: Client):
    service = ClientService(test_session)

    await service.delete(mock_client.id)

    assert mock_client not in await test_session.scalars(select(Client))
    assert await test_session.scalar(
        select(func.count()).where(Client.id == mock_client.id)) == 0


async def test_set_last_authenticated(test_session: AsyncSession, mock_client: Client):
    service = ClientService(test_session)
    new_date = datetime.now() + timedelta(days=120)
    old_date = mock_client.last_authenticated

    await service.set_last_authenticated(
        instance=mock_client,
        date=new_date
    )
    assert mock_client.last_authenticated == new_date

    assert await test_session.scalar(
        select(func.count()).where(
            Client.id == mock_client.id,
            Client.last_authenticated == old_date
        )) == 0
    assert await test_session.scalar(
        select(func.count()).where(
            Client.id == mock_client.id,
            Client.last_authenticated == new_date)) == 1
