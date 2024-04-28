from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import AppError
from models.base import Base


class ServiceError(AppError):
    pass


class UniquenessError(ServiceError):
    pass


class BaseService:
    pass


class ModelService(BaseService):
    model_cls = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, commit: bool = True, **kwargs) -> Base:
        raise NotImplementedError

    async def get_by_id(self, id_: int):
        return await self.session.scalar(
            select(self.model_cls).where(self.model_cls.id == id_)
        )

    async def delete(self, instance_id: int, commit: bool = True):
        qs = delete(self.model_cls).where(self.model_cls.id == instance_id)

        await self.session.execute(qs)
        if commit:
            await self.session.commit()
