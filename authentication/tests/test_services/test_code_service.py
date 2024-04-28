from datetime import datetime, timedelta

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.client import Client
from models.code import Code
from services.code_service import CodeService


async def test_create(test_session: AsyncSession, mock_client: Client):
    service = CodeService(test_session)
    valid_until = datetime.now() + timedelta(days=20)
    redirect_uri = "redirect_uri"

    code = await service.create(
        client=mock_client,
        redirect_uri=redirect_uri,
        valid_until=valid_until
    )

    assert code in await test_session.scalars(select(Code))
    assert await test_session.scalar(
        select(func.count())
        .where(Code.id == code.id)) == 1

    await test_session.execute(delete(Client).where(Code.id == code.id))
    await test_session.commit()


async def test_get_by_id(test_session: AsyncSession, mock_code: Code):
    service = CodeService(test_session)
    assert mock_code == await service.get_by_id(id_=mock_code.id)


async def test_get_by_id_not_exist(test_session: AsyncSession):
    non_existent_id = int(1e9 + 42)
    service = CodeService(test_session)
    assert not await service.get_by_id(id_=non_existent_id)


async def test_get_valid_code_success(test_session: AsyncSession, mock_code: Code):
    service = CodeService(test_session)
    assert mock_code == await service.get_valid_code(
        value=mock_code.value,
        client_id=mock_code.client.id,
        redirect_uri=mock_code.redirect_uri
    )


async def test_get_valid_code_wrong_value(test_session: AsyncSession, mock_code: Code):
    service = CodeService(test_session)
    assert not await service.get_valid_code(
        value="wrong_value",
        client_id=mock_code.client.id,
        redirect_uri=mock_code.redirect_uri
    )


async def test_get_valid_code_wrong_client_id(test_session: AsyncSession, mock_code: Code):
    service = CodeService(test_session)
    assert not await service.get_valid_code(
        value=mock_code.value,
        client_id=int(1e9) + 42,
        redirect_uri=mock_code.redirect_uri
    )


async def test_get_valid_code_wrong_valid_until(test_session: AsyncSession, mock_code: Code):
    service = CodeService(test_session)
    mock_code.valid_until = datetime.now() - timedelta(minutes=10)
    test_session.add(mock_code)
    await test_session.commit()

    assert not await service.get_valid_code(
        value=mock_code.value,
        client_id=mock_code.client.id,
        redirect_uri=mock_code.redirect_uri
    )
