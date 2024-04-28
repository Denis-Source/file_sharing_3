import pytest
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from services.base import UniquenessError
from services.user_service import UserService
from tests.conftest import generate_mock_plain_password, generate_mock_name


async def test_create(test_session: AsyncSession):
    service = UserService(test_session)

    user = await service.create(
        username=f"user_{generate_mock_name()}",
        plain_password=generate_mock_plain_password()
    )
    assert user in await test_session.scalars(select(User))
    assert await test_session.scalar(
        select(func.count())
        .where(User.id == user.id)) == 1

    await test_session.execute(delete(User).where(User.id == user.id))
    await test_session.commit()


async def test_get_by_id(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    assert mock_user == await service.get_by_id(id_=mock_user.id)


async def test_get_by_id_not_exist(test_session: AsyncSession):
    non_existent_id = int(1e9 + 42)
    service = UserService(test_session)
    assert not await service.get_by_id(id_=non_existent_id)


async def test_create_username_uniqueness(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    with pytest.raises(UniquenessError):
        await service.create(
            username=mock_user.username,
            plain_password=generate_mock_plain_password()
        )


async def test_delete(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)

    await service.delete(mock_user.id)

    assert mock_user not in await test_session.scalars(select(User))
    assert await test_session.scalar(
        select(func.count()).where(User.id == mock_user.id)) == 0


async def test_set_password(test_session: AsyncSession, mock_user: User):
    service = UserService(test_session)
    old_password = mock_user.password
    new_plain_password = generate_mock_plain_password()
    mock_user = await service.set_password(mock_user, new_plain_password)

    assert mock_user.password != new_plain_password
    assert await test_session.scalar(
        select(func.count()).where(
            User.id == mock_user.id,
            User.password == old_password
        )) == 0
    assert await test_session.scalar(
        select(func.count()).where(
            User.id == mock_user.id,
            User.password == mock_user.password
        )) == 1


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


async def test_get_user_by_username(test_session: AsyncSession, mock_user):
    service = UserService(test_session)
    assert mock_user == await service.get_user_by_username(mock_user.username)


async def test_get_user_by_username_not_exist(test_session: AsyncSession):
    service = UserService(test_session)
    non_existent_username = "non-existent-user"

    assert await service.get_user_by_username(non_existent_username) is None
