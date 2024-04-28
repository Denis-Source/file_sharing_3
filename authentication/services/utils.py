import base64
import secrets
from urllib.parse import urlencode


def encode64(input_bytes: bytes) -> str:
    return base64.b64encode(input_bytes).decode()


def decode64(input_str: str) -> bytes:
    return base64.b64decode(input_str)


def querify_url(url: str, **params) -> str:
    return f"{url}?{urlencode(params)}"


def generate_authorization_code(length: int = 32) -> str:
    return secrets.token_urlsafe(length)
