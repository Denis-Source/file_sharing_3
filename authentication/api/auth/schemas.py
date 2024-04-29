from typing import Annotated, Optional

from fastapi.params import Form
from pydantic import BaseModel as BaseSchema


class CredentialsRequest(BaseSchema):
    username: str
    password: str


class AuthorizationResponse(BaseSchema):
    redirect_uri: str


class PasswordTokenRequestForm:
    def __init__(
            self,
            *,
            username: Annotated[str, Form()],
            password: Annotated[str, Form()],
            client_id: Annotated[int, Form()],
            client_secret: Annotated[str, Form()]):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret


class CodeTokenRequest(BaseSchema):
    code: str
    client_id: int
    client_secret: str
    redirect_uri: str


class RefreshRequest(BaseSchema):
    refresh_token: str
    client_id: int
    client_secret: str


class VerifyRequest(BaseSchema):
    access_token: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: Optional[str]
    token_type: str
