from sqlalchemy import select

from models.scope import Scope
from services.base import ModelService, UniquenessError


class ScopeService(ModelService):
    model_cls = Scope

    async def create(self, type_: str, commit: bool = True, **kwargs) -> Scope:
        if await self.session.scalar(select(Scope).where(Scope.type == type_)):
            raise UniquenessError(f"Scope {type_} already exists")

        instance = Scope(
            type=type_,
            **kwargs
        )
        self.session.add(instance)
        if commit:
            await self.session.commit()
        return instance

    async def get_by_type(self, type_: str):
        return await self.session.scalar(
            select(self.model_cls).where(self.model_cls.type == type_)
        )
