import re
from datetime import timedelta, datetime

import jwt
from jwt import DecodeError

from config import APP_NAME
from env import get_app_secret
from services.base import BaseService

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


class HeaderValueError(ValueError):
    def __str__(self):
        return "Invalid JWT header"


class AuthenticationService(BaseService):
    def generate_header(self, token: str) -> str:
        return f"Authorization: Bearer {token}"

    def parse_header(self, header: str) -> str:
        if not re.compile(HEADER_REGEX).match(header):
            raise HeaderValueError

        return header.replace("Authorization: Bearer ", "")

    def generate_token(self, sub: str, secret: str = None, **params) -> str:
        if not secret:
            secret = get_app_secret()

        return jwt.encode(
            {
                "iss": APP_NAME,
                "sub": sub,
                "exp": datetime.utcnow() + timedelta(days=60),
                "iat": datetime.utcnow(),
                **params
            },
            secret,
            algorithm=JWT_ALGORITHM
        )

    def decode_token(self, token: str, secret: str = None) -> dict:
        if not secret:
            secret = get_app_secret()
        decoded_token = jwt.decode(
            token,
            secret,
            JWT_ALGORITHM
        )
        if "sub" not in decoded_token:
            raise DecodeError

        if "exp" not in decoded_token:
            raise DecodeError

        if decoded_token.get("iss") != APP_NAME:
            raise DecodeError

        return decoded_token
