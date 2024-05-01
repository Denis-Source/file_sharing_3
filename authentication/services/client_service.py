from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import subqueryload

from models.client import Client
from models.scope import Scope
from models.user import User
from services.base import ModelService, UniquenessError, ServiceError


class InvalidScopeError(ServiceError):
    def __init__(self):
        self.message = "Invalid scope"


class ClientService(ModelService):
    model_cls = Client

    async def _preload_relationships(self, instance: Client):
        return await self.session.scalar(
            select(Client)
            .where(Client.id == instance.id)
            .options(subqueryload(self.model_cls.user))
            .options(subqueryload(self.model_cls.scopes))
        )

    async def create(
            self,
            name: str,
            user: User,
            scopes: list[Scope.Types] = None,
            commit: bool = True,
            **kwargs) -> Client:
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

        if scopes:
            await self.set_scopes(
                instance=instance,
                scopes=scopes,
            )

        return instance

    async def get_client_by_secret(self, secret: str) -> Client:
        client = await self.session.scalar(
            select(Client).where(Client.secret == secret)
        )
        if client:
            client = await self._preload_relationships(client)
        return client

    async def set_last_authenticated(self, instance: Client, date: datetime = None, commit: bool = True) -> Client:
        if not date:
            date = datetime.now()

        instance.last_authenticated = date
        self.session.add(instance)
        if commit:
            await self.session.commit()

        return instance

    async def set_scopes(self, instance: Client, scopes: [Scope.Types], commit=True) -> Client:
        scope_instances = (await self.session.scalars(
            select(Scope).where(Scope.type.in_(scopes))
        )).all()

        if set([scope.type for scope in scope_instances]) != set(scopes):
            raise InvalidScopeError

        for scope in scope_instances:
            instance.scopes.add(scope)
        self.session.add(instance)
        if commit:
            await self.session.commit()

        return instance
