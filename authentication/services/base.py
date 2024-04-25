from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import AppError
from models.base import Base


class BaseService:
    pass


class ModelService(BaseService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, commit: bool = True, **kwargs) -> Base:
        raise NotImplementedError

    async def delete(self, instance_id: int, commit: bool = True):
        raise NotImplementedError


class ServiceError(AppError):
    pass


class UniquenessError(ServiceError):
    pass
