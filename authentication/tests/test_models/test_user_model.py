import pytest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import FieldValidationError
from models.user import User
from tests.conftest import generate_mock_email, generate_mock_password


async def test_create(test_session: AsyncSession):
    email = generate_mock_email()
    password = generate_mock_password()
    user = User(
        email=email,
        password=password
    )
    test_session.add(user)
    await test_session.commit()

    assert user in await test_session.scalars(select(User))

    await test_session.execute(delete(User).where(User.id == user.id))
    await test_session.commit()


async def test_email_constraint(test_session: AsyncSession):
    password = generate_mock_password()

    user = User(
        password=password
    )
    test_session.add(user)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_password_constraint(test_session: AsyncSession):
    email = generate_mock_email()

    user = User(
        email=email
    )
    test_session.add(user)
    with pytest.raises(IntegrityError):
        await test_session.commit()
    await test_session.rollback()


async def test_email_validation():
    not_valid_email = "not_valid"
    password = generate_mock_password()

    with pytest.raises(FieldValidationError):
        User(
            email=not_valid_email,
            password=password
        )


async def test_password_validation():
    email = generate_mock_email()
    not_valid_password = "not_valid$password"

    with pytest.raises(FieldValidationError):
        User(
            email=email,
            password=not_valid_password
        )


async def test_delete(test_session: AsyncSession, mock_user: User):
    qs = delete(User).where(User.id == mock_user.id)
    await test_session.execute(qs)

    assert mock_user not in await test_session.scalars(select(User))
