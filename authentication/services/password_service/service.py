import os
from enum import Enum
from typing import List

from services.base import BaseService
from services.password_service.algorithms import get_plain_hash, get_sha256_hash
from services.utils import encode64, decode64


class PasswordAlgorithms(str, Enum):
    PLAIN = "plain"
    SHA256 = "sha256"


ALGORITHM_MAP = {
    PasswordAlgorithms.PLAIN: get_plain_hash,
    PasswordAlgorithms.SHA256: get_sha256_hash
}


class PasswordService(BaseService):
    def generate_salt(self, length: int = 16) -> bytes:
        return os.urandom(length)

    def format_password(self, algorithm: str, iterations: int, hash_: str, salt: str):
        return f"{algorithm}${iterations}${hash_}${salt}"

    def validate(self, plain_password: str, validators: List[callable]):
        for validator in validators:
            validator(plain_password)

    def get_algorithm_fn(self, algorithm: PasswordAlgorithms) -> callable:
        algorithm_fn = ALGORITHM_MAP.get(algorithm)
        if not algorithm_fn:
            raise NotImplementedError

        return algorithm_fn

    def get_hash(
            self,
            plain_password: str,
            algorithm_fn: callable,
            iterations: int,
            salt: bytes = None) -> bytes:
        return algorithm_fn(
            plain_password=plain_password,
            iterations=iterations,
            salt=salt
        )

    def hash_password(
            self,
            plain_password: str,
            algorithm: PasswordAlgorithms,
            iterations: int,
            salt: bytes = None) -> str:
        if salt is None:
            salt = self.generate_salt()

        algorithm_fn = self.get_algorithm_fn(algorithm)

        hash_ = self.get_hash(
            plain_password=plain_password,
            algorithm_fn=algorithm_fn,
            iterations=iterations,
            salt=salt
        )
        return self.format_password(
            algorithm=algorithm,
            iterations=iterations,
            hash_=encode64(hash_),
            salt=encode64(salt)
        )

    def check_password(self, plain_password: str, password: str) -> bool:
        algorithm, iterations, hash_, salt = password.split("$")
        algorithm_fn = self.get_algorithm_fn(algorithm)

        expected_hash = self.get_hash(
            plain_password=plain_password,
            algorithm_fn=algorithm_fn,
            iterations=int(iterations),
            salt=decode64(salt)
        )
        return expected_hash == decode64(hash_)
