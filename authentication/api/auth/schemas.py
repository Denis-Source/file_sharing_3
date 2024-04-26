from datetime import datetime

from pydantic import BaseModel as BaseSchema


class RegisterRequest(BaseSchema):
    username: str
    password: str


class RegisterResponse(BaseSchema):
    id: int
    username: str
    created_at: datetime


class Token(BaseSchema):
    access_token: str
    token_type: str
