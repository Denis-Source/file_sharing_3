from datetime import timedelta, datetime
from enum import Enum
from urllib.parse import urljoin

import jwt
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from config import APP_NAME
from env import get_app_secret, get_frontend_url, get_authentication_code_valid_minutes, get_access_token_valid, \
    get_refresh_token_valid
from models.code import Code
from models.user import User
from services.base import BaseService, ServiceError
from services.client_service import ClientService
from services.code_service import CodeService
from services.user_service import UserService
from services.utils import querify_url

JWT_ALGORITHM = "HS256"
JWT_REGEX = r"[\w-]*\.[\w-]*\.[\w-]*"
HEADER_REGEX = f"^Authorization: Bearer {JWT_REGEX}$"

OPTIONS = {
    "verify_signature": True,
    "verify_exp": True,
    "verify_nbf": False,
    "verify_iat": True,
    "verify_aud": False
}

TOKEN_ISS = "iss"
TOKEN_SUB = "sub"
TOKEN_EXP = "exp"
TOKEN_IAT = "iat"
TOKEN_TYPE = "type"


class TokenTypes(str, Enum):
    REFRESH = "refresh"
    ACCESS = "access"


class AuthenticationError(ServiceError):
    pass


class TokenError(AuthenticationError):
    def __init__(self):
        self.message = "Token error"


class AuthenticationService(BaseService):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def get_expiration_date(type_: TokenTypes) -> datetime:
        match type_:
            case TokenTypes.ACCESS:
                return datetime.utcnow() + get_access_token_valid()
            case TokenTypes.REFRESH:
                return datetime.utcnow() + get_refresh_token_valid()

    @staticmethod
    def generate_token(
            sub: str,
            type_: TokenTypes = TokenTypes.ACCESS,
            secret: str = None,
            **params) -> str:
        if not secret:
            secret = get_app_secret()

        return jwt.encode(
            {
                TOKEN_SUB: sub,
                TOKEN_ISS: APP_NAME,
                TOKEN_IAT: datetime.utcnow().timestamp(),
                TOKEN_EXP: AuthenticationService.get_expiration_date(type_).timestamp(),
                TOKEN_TYPE: type_,
                **params
            },
            secret,
            algorithm=JWT_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str, secret: str = None) -> dict:
        if not secret:
            secret = get_app_secret()

        try:
            decoded_token = jwt.decode(
                token,
                secret,
                JWT_ALGORITHM
            )
        except InvalidTokenError as e:
            raise TokenError from e

        if TOKEN_SUB not in decoded_token or TOKEN_EXP not in decoded_token:
            raise TokenError

        if decoded_token.get(TOKEN_ISS) != APP_NAME:
            raise TokenError

        return decoded_token

    async def create_password_pair(
            self,
            username: str,
            password: str,
            client_id: int,
            client_secret: str,
            secret: str = None
    ) -> tuple[str, str]:
        if not secret:
            secret = get_app_secret()

        user_service = UserService(self.session)
        user = await user_service.get_user_by_username(username)
        if not user:
            raise AuthenticationError("User not found")
        if not await user_service.check_password(user, password):
            raise AuthenticationError("Incorrect password")

        client_service = ClientService(self.session)
        client = await client_service.get_client_by_secret(client_secret)
        if not client:
            raise AuthenticationError("Incorrect secret")
        if client.id != client_id:
            raise AuthenticationError("Incorrect client id")
        if client.user.id != user.id:
            raise AuthenticationError("Wrong user")

        access_token = self.generate_token(
            sub=user.username,
            type_=TokenTypes.ACCESS,
            secret=secret
        )
        refresh = self.generate_token(
            sub=user.username,
            type_=TokenTypes.REFRESH,
            secret=secret
        )

        return access_token, refresh

    async def get_user_by_token(
            self,
            token: str,
            required_token_type=TokenTypes.ACCESS,
            secret: str = None) -> User:
        user_service = UserService(self.session)
        decoded_token = self.decode_token(token, secret)

        username = decoded_token.get("sub")
        token_type = decoded_token.get("type")
        if token_type != required_token_type:
            raise AuthenticationError("Token should be of access type")

        user = await user_service.get_user_by_username(username=username)
        if not user:
            raise AuthenticationError("User not found")

        return user

    async def authenticate_user(self, username: str, password: str) -> User:
        user_service = UserService(self.session)
        user = await user_service.get_user_by_username(username)
        if not user:
            raise AuthenticationError("User not found")
        if not await user_service.check_password(user, password):
            raise AuthenticationError("Wrong password")

        return user

    @staticmethod
    def get_auth_uri(client_id: int, redirect_uri: str) -> str:
        return querify_url(
            url=urljoin(get_frontend_url(), "login/"),
            client_id=client_id,
            redirect_uri=redirect_uri
        )

    @staticmethod
    def get_callback_uri(code: Code) -> str:
        return querify_url(
            url=code.redirect_uri,
            code=code.value
        )

    async def generate_code(self, client_id: int, redirect_uri: str) -> Code:
        code_service = CodeService(self.session)
        client_service = ClientService(self.session)
        client = await client_service.get_by_id(client_id)
        if not client:
            raise AuthenticationError("Invalid client id")

        return await code_service.create(
            client=client,
            redirect_uri=redirect_uri,
            valid_until=datetime.now() + timedelta(minutes=get_authentication_code_valid_minutes())
        )

    async def check_code(
            self,
            client_id: int,
            client_secret: str,
            redirect_uri: str,
            value: str
    ) -> Code:
        client_service = ClientService(self.session)
        client = await client_service.get_client_by_secret(client_secret)

        if not client:
            raise AuthenticationError("Invalid client secret")
        if client.id != client_id:
            raise AuthenticationError("Invalid client id")

        code_service = CodeService(self.session)
        code = await code_service.get_valid_code(value, client.id, redirect_uri)
        if not code:
            raise AuthenticationError("Invalid code")

        return code

    async def create_code_pair(
            self,
            client_id: int,
            client_secret: str,
            redirect_uri: str,
            value: str,
            secret: str = None
    ) -> tuple[str, str]:
        code = await self.check_code(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            value=value
        )
        if not secret:
            secret = get_app_secret()

        access_token = self.generate_token(
            sub=code.client.user.username,
            type_=TokenTypes.ACCESS,
            secret=secret
        )
        refresh = self.generate_token(
            sub=code.client.user.username,
            type_=TokenTypes.REFRESH,
            secret=secret
        )

        return access_token, refresh

    async def refresh_pair(
            self,
            refresh_token: str,
            client_id: int,
            client_secret: str,
            secret: str = None
    ) -> tuple[str, str]:
        if not secret:
            secret = get_app_secret()

        client_service = ClientService(self.session)
        client = await client_service.get_client_by_secret(secret=client_secret)

        if not client:
            raise AuthenticationError("Invalid client secret")
        if client.id != client_id:
            raise AuthenticationError("Invalid client id")

        user = await self.get_user_by_token(
            token=refresh_token,
            required_token_type=TokenTypes.REFRESH,
            secret=secret
        )

        access_token = self.generate_token(
            sub=user.username,
            type_=TokenTypes.ACCESS,
            secret=secret
        )
        refresh = self.generate_token(
            sub=user.username,
            type_=TokenTypes.REFRESH,
            secret=secret
        )
        return access_token, refresh
