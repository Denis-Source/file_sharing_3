import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.scope import Scope
from tests.conftest import generate_mock_name


async def test_create(test_session: AsyncSession):
    type_ = f"scope_{generate_mock_name()}"
    scope = Scope(
        type=type_
    )
    test_session.add(scope)
    await test_session.commit()

    assert scope in await test_session.scalars(select(Scope))

    await test_session.execute(delete(Scope).where(Scope.id == scope.id))
    await test_session.commit()


async def test_type_constraint(test_session: AsyncSession):
    scope = Scope(
    )
    test_session.add(scope)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_type_uniqueness(test_session: AsyncSession, mock_scope: Scope):
    scope = Scope(
        type=mock_scope.type
    )
    test_session.add(scope)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_delete(test_session: AsyncSession, mock_scope: Scope):
    qs = delete(Scope).where(Scope.id == mock_scope.id)
    await test_session.execute(qs)

    assert mock_scope not in await test_session.scalars(select(Scope))
