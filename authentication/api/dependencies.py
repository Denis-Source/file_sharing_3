from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_session
from services.authentication_serivce import AuthenticationService
from services.client_service import ClientService
from services.user_service import UserService


async def get_auth_service(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> AuthenticationService:
    async with session:
        return AuthenticationService(session)


async def get_user_service(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> UserService:
    async with session:
        return UserService(session)


async def get_client_service(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> ClientService:
    async with session:
        return ClientService(session)
