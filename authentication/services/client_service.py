from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import subqueryload

from models.client import Client
from models.user import User
from services.base import ModelService, UniquenessError


class ClientService(ModelService):
    model_cls = Client

    async def _preload_relationships(self, instance: Client):
        return await self.session.scalar(
            select(Client)
            .where(Client.id == instance.id)
            .options(subqueryload(self.model_cls.user))
        )

    async def create(self, name: str, user: User, commit: bool = True, **kwargs) -> Client:
        if await self.session.scalar(select(Client).where(Client.name == name)):
            raise UniquenessError(f"Client with name {name} already exists")

        instance = Client(
            name=name,
            user=user,
            **kwargs
        )
        self.session.add(instance)
        if commit:
            await self.session.commit()
            instance = await self._preload_relationships(instance)
        return instance

    async def get_client_by_secret(self, secret: str) -> Client:
        return await self.session.scalar(
            select(Client).where(Client.secret == secret)
        )

    async def set_last_authenticated(self, instance: Client, date: datetime = None, commit: bool = True) -> Client:
        if not date:
            date = datetime.now()

        instance.last_authenticated = date
        self.session.add(instance)
        if commit:
            await self.session.commit()

        return instance
