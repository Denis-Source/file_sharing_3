from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import get_password_iterations, get_password_algorithm, get_password_validators
from models.user import User
from services.base import ModelService, UniquenessError
from services.password_service.service import PasswordService


class UserService(ModelService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def _preload_relationships(self, instance: User) -> User:
        return await self.session.scalar(
            select(User)
            .where(User.id == instance.id)
            .options(selectinload(User.clients)))

    async def create(self, username: str, plain_password: str, commit: bool = True, **kwargs) -> User:
        if await self.session.scalar(select(User).where(User.username == username)):
            raise UniquenessError(f"User with username {username} already exists")

        validators = get_password_validators()
        iterations = get_password_iterations()
        algorithm = get_password_algorithm()

        password_service = PasswordService()

        password_service.validate(
            plain_password=plain_password,
            validators=validators
        )
        formatted_password = password_service.hash_password(
            plain_password=plain_password,
            algorithm=algorithm,
            iterations=iterations
        )

        instance = User(
            username=username,
            password=formatted_password,
            **kwargs
        )
        self.session.add(instance)
        if commit:
            await self.session.commit()
            instance = await self._preload_relationships(instance)
        return instance

    async def delete(self, instance_id: int, commit: bool = True):
        qs = delete(User).where(User.id == instance_id)

        await self.session.execute(qs)
        if commit:
            await self.session.commit()

    async def set_password(self, instance: User, plain_password: str, commit: bool = True) -> User:
        validators = get_password_validators()
        iterations = get_password_iterations()
        algorithm = get_password_algorithm()

        password_service = PasswordService()

        password_service.validate(
            plain_password=plain_password,
            validators=validators
        )
        formatted_password = password_service.hash_password(
            plain_password=plain_password,
            algorithm=algorithm,
            iterations=iterations
        )
        instance.password = formatted_password
        self.session.add(instance)
        if commit:
            await self.session.commit()

        return instance

    async def check_password(self, instance: User, plain_password: str) -> bool:
        password_service = PasswordService()

        return password_service.check_password(
            password=instance.password,
            plain_password=plain_password
        )

    async def get_user_by_username(self, username: str) -> User:
        return await self.session.scalar(select(User).where(User.username == username))
