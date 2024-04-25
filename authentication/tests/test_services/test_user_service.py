import re

import pytest
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from services.authentication_serivce import JWT_REGEX, AuthenticationService
from services.base import UniquenessError
from services.user_service import UserService
from tests.conftest import generate_mock_plain_password, generate_mock_email


async def test_create(test_session: AsyncSession):
    service = UserService(test_session)

    user = await service.create(
        email=generate_mock_email(),
        plain_password=generate_mock_plain_password()
    )
    assert user in await test_session.scalars(select(User))
    assert await test_session.scalar(
        select(func.count())
        .where(User.id == user.id)) == 1

    await test_session.execute(delete(User).where(User.id == user.id))
    await test_session.commit()


async def test_create_email_uniqueness(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    with pytest.raises(UniquenessError):
        await service.create(
            email=mock_user.email,
            plain_password=generate_mock_plain_password()
        )


async def test_delete(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)

    await service.delete(mock_user.id)

    assert mock_user not in await test_session.scalars(select(User))
    assert await test_session.scalar(
        select(func.count()).where(User.id == mock_user.id)) == 0


async def test_set_email(test_session: AsyncSession, mock_user: User):
    old_email = mock_user.email
    new_email = generate_mock_email(domain="new-domain.com")

    service = UserService(test_session)

    await service.set_email(
        instance=mock_user,
        email=new_email
    )

    assert mock_user.email == new_email
    assert await test_session.scalar(
        select(func.count()).where(User.email == old_email)) == 0
    assert await test_session.scalar(
        select(func.count()).where(User.email == new_email)) == 1


async def test_set_email_already_exists(test_session: AsyncSession, mock_user: User):
    old_email = mock_user.email

    service = UserService(test_session)

    with pytest.raises(UniquenessError):
        await service.set_email(
            instance=mock_user,
            email=old_email
        )


async def test_set_password(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    old_password = mock_user.password
    new_plain_password = generate_mock_plain_password()
    mock_user = await service.set_password(mock_user, new_plain_password)

    assert mock_user.password != new_plain_password
    assert await test_session.scalar(
        select(func.count()).where(User.password == old_password)) == 0
    assert await test_session.scalar(
        select(func.count()).where(User.password == mock_user.password)) == 1


async def test_check_password_correct(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    new_plain_password = generate_mock_plain_password()
    mock_user = await service.set_password(mock_user, new_plain_password)

    check = await service.check_password(mock_user, new_plain_password)
    assert check


async def test_check_password_not_correct(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    new_plain_password = generate_mock_plain_password()
    mock_user = await service.set_password(mock_user, new_plain_password)

    check = await service.check_password(mock_user, "not_correct_password")
    assert not check


async def test_generate_token(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    token = await service.generate_token(mock_user)

    assert re.compile(JWT_REGEX).match(token)


async def test_get_user_by_email(test_session: AsyncSession, mock_user):
    service = UserService(test_session)
    assert mock_user == await service.get_user_by_email(mock_user.email)


async def test_get_user_by_email_not_exist(test_session: AsyncSession):
    service = UserService(test_session)
    non_existent_email = generate_mock_email()

    assert await service.get_user_by_email(non_existent_email) is None


async def test_get_user_by_token(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    authentication_service = AuthenticationService()
    token = authentication_service.generate_token(sub=mock_user.id)

    assert mock_user == await service.get_user_by_token(token)


async def test_get_user_by_token_not_exist(test_session: AsyncSession):
    non_existent_user_id = 123
    service = UserService(test_session)
    authentication_service = AuthenticationService()
    token = authentication_service.generate_token(sub=non_existent_user_id)

    assert await service.get_user_by_token(token) is None
