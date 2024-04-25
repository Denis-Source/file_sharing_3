import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import FieldValidationError
from models.user import User
from tests.conftest import generate_mock_password, generate_mock_name


async def test_create(test_session: AsyncSession):
    username = f"user_{generate_mock_name()}"
    password = generate_mock_password()
    user = User(
        username=username,
        password=password
    )
    test_session.add(user)
    await test_session.commit()

    assert user in await test_session.scalars(select(User))

    await test_session.execute(delete(User).where(User.id == user.id))
    await test_session.commit()


async def test_username_constraint(test_session: AsyncSession):
    password = generate_mock_password()

    user = User(
        password=password
    )
    test_session.add(user)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_password_constraint(test_session: AsyncSession):
    username = f"user_{generate_mock_name()}"

    user = User(
        username=username
    )
    test_session.add(user)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_username_validation():
    not_valid_username = "not_valid@asd!!"
    password = generate_mock_password()

    with pytest.raises(FieldValidationError):
        User(
            username=not_valid_username,
            password=password
        )


async def test_password_validation():
    username = f"user-{generate_mock_name()}"
    not_valid_password = "not_valid$password"

    with pytest.raises(FieldValidationError):
        User(
            username=username,
            password=not_valid_password
        )


async def test_delete(test_session: AsyncSession, mock_user: User):
    qs = delete(User).where(User.id == mock_user.id)
    await test_session.execute(qs)

    assert mock_user not in await test_session.scalars(select(User))
