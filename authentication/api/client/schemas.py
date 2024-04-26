from datetime import datetime

from pydantic import BaseModel as BaseSchema


class RegisterClientRequest(BaseSchema):
    username: str
    client_name: str


class RegisterClientResponse(BaseSchema):
    id: int
    name: str
    secret: str
    created_at: datetime
