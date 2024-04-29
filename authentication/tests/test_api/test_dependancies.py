from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_auth_service, get_user_service, get_client_service
from services.authentication_serivce import AuthenticationService
from services.client_service import ClientService
from services.user_service import UserService


async def test_get_auth_service(test_session: AsyncSession):
    auth_service = await get_auth_service(test_session)
    assert isinstance(auth_service, AuthenticationService)


async def test_get_user_service(test_session: AsyncSession):
    auth_service = await get_user_service(test_session)
    assert isinstance(auth_service, UserService)


async def test_get_client_service(test_session: AsyncSession):
    auth_service = await get_client_service(test_session)
    assert isinstance(auth_service, ClientService)
