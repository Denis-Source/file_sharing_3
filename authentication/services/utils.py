import base64


def encode64(input_bytes: bytes) -> str:
    return base64.b64encode(input_bytes).decode()


def decode64(input_str: str) -> bytes:
    return base64.b64decode(input_str)
