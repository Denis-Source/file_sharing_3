from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.scope import Scope
from services.scope_service import ScopeService
from tests.conftest import generate_mock_name


async def test_create(test_session: AsyncSession):
    service = ScopeService(test_session)

    scope = await service.create(
        type_=f"scope-{generate_mock_name()}"
    )
    assert scope in await test_session.scalars(select(Scope))
    assert await test_session.scalar(
        select(func.count())
        .where(Scope.id == scope.id)) == 1

    await test_session.execute(delete(Scope).where(Scope.id == scope.id))
    await test_session.commit()


async def test_get_by_id(test_session: AsyncSession, mock_scope: Scope):
    service = ScopeService(test_session)
    assert mock_scope == await service.get_by_id(id_=mock_scope.id)


async def test_get_by_type(test_session: AsyncSession, mock_scope: Scope):
    service = ScopeService(test_session)
    assert mock_scope == await service.get_by_type(type_=mock_scope.type)


async def test_delete(test_session: AsyncSession, mock_scope: Scope):
    service = ScopeService(test_session)

    await service.delete(mock_scope.id)

    assert mock_scope not in await test_session.scalars(select(Scope))
    assert await test_session.scalar(
        select(func.count()).where(Scope.id == mock_scope.id)) == 0
