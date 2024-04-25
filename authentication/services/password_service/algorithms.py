import hashlib


def get_plain_hash(plain_password: str, iterations: int, salt: bytes) -> bytes:
    return plain_password.encode()


def get_sha256_hash(plain_password: str, iterations: int, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=plain_password.encode(),
        salt=salt,
        iterations=iterations
    )
