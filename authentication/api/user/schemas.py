from datetime import datetime

from pydantic import BaseModel as BaseSchema, EmailStr


class UserResponse(BaseSchema):
    id: int
    username: str
    created_at: datetime


class SetPasswordRequest(BaseSchema):
    new_password: str
