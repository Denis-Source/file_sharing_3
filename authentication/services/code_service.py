from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.orm import subqueryload

from models.client import Client
from models.code import Code
from services.base import ModelService
# TODO test
from services.utils import generate_authorization_code


class CodeService(ModelService):
    # TODO make it automatically for all model selects
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

    async def delete(self, instance_id: int, commit: bool = True):
        qs = delete(Code).where(Code.id == instance_id)

        await self.session.execute(qs)
        if commit:
            await self.session.commit()

    async def get_valid_code(self, value: str, client_id: int, redirect_uri: str) -> Code:
        code = await self.session.scalar(
            select(Code).where(
                Code.value == value,
                Code.client_id == client_id,
                Code.redirect_uri == redirect_uri,
                Code.valid_until > datetime.now()
            )
        )
        # TODO fix that
        if code:
            code = await self._preload_relationships(code)
        return code
