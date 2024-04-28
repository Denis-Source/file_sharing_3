from datetime import datetime, timedelta

import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.client import Client
from models.code import Code
from tests.conftest import get_mock_callback_uri


async def test_create(test_session: AsyncSession, mock_client: Client):
    code = Code(
        value="test_value",
        client_id=mock_client.id,
        redirect_uri=get_mock_callback_uri(),
        valid_until=datetime.now() + timedelta(minutes=10)
    )
    test_session.add(code)
    await test_session.commit()

    assert code in await test_session.scalars(select(Code))

    await test_session.execute(delete(Code).where(Code.id == code.id))
    await test_session.commit()


async def test_client_id_constraint(test_session: AsyncSession):
    code = Code(
        value="test_value",
        redirect_uri=get_mock_callback_uri(),
        valid_until=datetime.now() + timedelta(minutes=10)
    )
    test_session.add(code)

    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_value_constraint(test_session: AsyncSession, mock_client: Client):
    code = Code(
        client_id=mock_client.id,
        redirect_uri=get_mock_callback_uri(),
        valid_until=datetime.now() + timedelta(minutes=10)
    )
    test_session.add(code)

    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_redirect_uri_constraint(test_session: AsyncSession, mock_client: Client):
    code = Code(
        client_id=mock_client.id,
        value="test_value",
        valid_until=datetime.now() + timedelta(minutes=10)
    )
    test_session.add(code)

    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_valid_until_constraint(test_session: AsyncSession, mock_client: Client):
    code = Code(
        value="test_value",
        client_id=mock_client.id,
        redirect_uri=get_mock_callback_uri(),
    )
    test_session.add(code)

    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_delete(test_session: AsyncSession, mock_code: Code):
    qs = delete(Code).where(Code.id == mock_code.id)
    await test_session.execute(qs)

    assert mock_code not in await test_session.scalars(select(Client))
