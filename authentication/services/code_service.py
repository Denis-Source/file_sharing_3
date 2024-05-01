from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import subqueryload

from models.client import Client
from models.code import Code
from services.base import ModelService
from services.utils import generate_authorization_code


class CodeService(ModelService):
    model_cls = Code

    async def _preload_relationships(self, instance: Code):
        return await self.session.scalar(
            select(Code)
            .where(Code.id == instance.id)
            .options(subqueryload(Code.client).subqueryload(Client.user))
        )

    async def create(
            self,
            client: Client,
            redirect_uri: str,
            valid_until: datetime,
            commit: bool = True,
            **kwargs) -> Code:
        instance = Code(
            client_id=client.id,
            redirect_uri=redirect_uri,
            valid_until=valid_until,
            value=generate_authorization_code(),
            **kwargs
        )
        self.session.add(instance)
        if commit:
            await self.session.commit()
            instance = await self._preload_relationships(instance)
        return instance

    async def set_is_used(self, instance: Code, is_used: bool = True, commit: bool = True) -> Code:
        instance.is_used = is_used
        self.session.add(instance)
        if commit:
            await self.session.commit()

        return instance

    async def get_valid_code(self, value: str, client_id: int, redirect_uri: str) -> Code:
        code = await self.session.scalar(
            select(Code).where(
                Code.value == value,
                Code.client_id == client_id,
                Code.redirect_uri == redirect_uri,
                Code.is_used == False,  # noqa E712
                Code.valid_until > datetime.now()
            )
        )
        if code:
            code = await self._preload_relationships(code)
        return code
