from datetime import datetime

from pydantic import BaseModel as BaseSchema

from models.scope import Scope


class RegisterClientRequest(BaseSchema):
    username: str
    client_name: str
    scopes: list[Scope.Types]


class RegisterClientResponse(BaseSchema):
    id: int
    name: str
    secret: str
    created_at: datetime
