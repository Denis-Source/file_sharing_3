from datetime import datetime

import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.client import Client
from models.user import User


async def test_create(test_session: AsyncSession, mock_user: User):
    last_authenticated = datetime.now()
    client = Client(
        last_authenticated=last_authenticated,
        user_id=mock_user.id
    )
    test_session.add(client)
    await test_session.commit()

    assert client in await test_session.scalars(select(Client))

    await test_session.execute(delete(Client).where(Client.id == client.id))
    await test_session.commit()


async def test_user_id_constraint(test_session: AsyncSession):
    last_authenticated = datetime.now()
    client = Client(
        last_authenticated=last_authenticated,
    )
    test_session.add(client)

    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_delete(test_session: AsyncSession, mock_client: Client):
    qs = delete(Client).where(Client.id == mock_client.id)
    await test_session.execute(qs)

    assert mock_client not in await test_session.scalars(select(Client))
