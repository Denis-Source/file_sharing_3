from fastapi.security import APIKeyHeader
from pydantic import BaseModel as BaseSchema


class HTTPExceptionSchema(BaseSchema):
    detail: str


class MessageSchema(BaseSchema):
    detail: str


jwt_schema = APIKeyHeader(name="Bearer")
