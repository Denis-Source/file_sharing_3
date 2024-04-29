from fastapi.security import APIKeyHeader
from pydantic import BaseModel as BaseSchema


class ErrorSchema(BaseSchema):
    detail: str


class MessageResponse(BaseSchema):
    detail: str


jwt_schema = APIKeyHeader(name="Bearer")
