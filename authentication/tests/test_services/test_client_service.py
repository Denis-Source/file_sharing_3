from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.client import Client, ClientScope
from models.scope import Scope
from models.user import User
from services.base import UniquenessError
from services.client_service import ClientService, InvalidScopeError
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


async def test_create_with_scopes(test_session: AsyncSession, mock_user: User, mock_scope: Scope):
    service = ClientService(test_session)
    name = f"client_{generate_mock_name()}"

    client = await service.create(
        name=name,
        user=mock_user,
        scopes=[mock_scope.type]
    )
    assert client in await test_session.scalars(select(Client))

    assert await test_session.scalar(
        select(func.count())
        .where(Client.id == client.id)) == 1
    assert await test_session.scalar(
        select(func.count())
        .where(ClientScope.client_id == client.id, ClientScope.scope_id == mock_scope.id)
    )

    await test_session.execute(delete(Client).where(Client.id == client.id))
    await test_session.commit()


async def test_get_by_id(test_session: AsyncSession, mock_client: Client):
    service = ClientService(test_session)
    assert mock_client == await service.get_by_id(id_=mock_client.id)


async def test_get_by_id_not_exist(test_session: AsyncSession):
    non_existent_id = int(1e9 + 42)
    service = ClientService(test_session)
    assert not await service.get_by_id(id_=non_existent_id)


async def test_name_uniqueness(test_session: AsyncSession, mock_user: User, mock_client: Client):
    service = ClientService(test_session)

    with pytest.raises(UniquenessError):
        await service.create(
            name=mock_client.name,
            user=mock_user
        )


async def test_get_client_by_secret_success(test_session: AsyncSession, mock_client: Client):
    service = ClientService(test_session)
    assert mock_client.id == (await service.get_client_by_secret(mock_client.secret)).id


async def test_get_client_by_secret_not_exist(test_session: AsyncSession):
    non_existent_secret = "non_existent_secret"
    service = ClientService(test_session)
    assert not await service.get_client_by_secret(non_existent_secret)


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


async def test_delete(test_session: AsyncSession, mock_client: Client):
    service = ClientService(test_session)

    await service.delete(mock_client.id)

    assert mock_client not in await test_session.scalars(select(Client))
    assert await test_session.scalar(
        select(func.count()).where(Client.id == mock_client.id)) == 0


async def test_set_scopes_success(test_session: AsyncSession, mock_client: Client, mock_scope: Scope):
    service = ClientService(test_session)

    await service.set_scopes(
        instance=mock_client,
        scopes=[mock_scope.type]
    )

    assert mock_scope in mock_client.scopes
    assert await test_session.scalar(
        select(func.count()).where(
            ClientScope.scope_id == mock_scope.id and ClientScope.client_id == mock_client.id
        )
    ) == 1


async def test_set_scopes_invalid_scope(test_session: AsyncSession, mock_client: Client, mock_scope: Scope):
    service = ClientService(test_session)
    non_existent_scope = "non_existent_scope"

    with pytest.raises(InvalidScopeError):
        await service.set_scopes(
            instance=mock_client,
            scopes=[non_existent_scope]
        )
