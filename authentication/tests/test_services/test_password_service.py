import hashlib
from random import randbytes

import pytest

from services.password_service.algorithms import get_plain_hash, get_sha256_hash
from services.password_service.service import PasswordAlgorithms, PasswordService
from services.password_service.validators import validate_min_length, PasswordValidationError, validate_max_length
from tests.conftest import generate_mock_plain_password
from tests.test_services.conftest import CORRECT_PASSWORD_MIN_LENGTH, CORRECT_PASSWORD_MAX_LENGTH


def test_plain_algorithm():
    plain_password = generate_mock_plain_password()
    hash_ = get_plain_hash(
        plain_password=plain_password,
        iterations=1,
        salt=b""
    )
    assert plain_password == hash_.decode()


def test_sha256_hash():
    plain_password = generate_mock_plain_password()
    salt = randbytes(16)
    iterations = 1000

    hash_ = get_sha256_hash(
        plain_password=plain_password,
        iterations=iterations,
        salt=salt
    )
    expected_hash = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=plain_password.encode(),
        salt=salt,
        iterations=iterations
    )

    assert hash_ == expected_hash


def test_generate_salt():
    password_service = PasswordService()
    salt_length = 24

    salt = password_service.generate_salt(salt_length)
    assert len(salt) == salt_length


@pytest.mark.parametrize(
    "algorithm, expected_fn", [
        (PasswordAlgorithms.PLAIN, get_plain_hash),
        (PasswordAlgorithms.SHA256, get_sha256_hash)
    ])
def test_algorithm_fn(algorithm: PasswordAlgorithms, expected_fn: callable):
    password_service = PasswordService()
    assert password_service.get_algorithm_fn(algorithm=algorithm) == expected_fn


def test_algorithm_fn_not_implemented():
    password_service = PasswordService()
    with pytest.raises(NotImplementedError):
        password_service.get_algorithm_fn("not_implemented_algorithm")


@pytest.mark.parametrize(
    "plain_password, algorithm_fn, iterations, salt, expected_result",
    [
        ("test_password", get_plain_hash, 1, b"salt",
         b"test_password"),
        ("test_password", get_sha256_hash, 1, b"salt",
         b"B\x1cp\x9d\xc9\x0e4\xcd\xbb\x1a\xd4.9K\x93\xe1\xd2(\xd3\xe6\x86\xcb\x8e\xc1m\xe5\x9b\xfe\xaf;\x98\xd6"),
        ("test_password", get_sha256_hash, 1000, b"salt",
         b"\xb2\xf3\xd3jQ9H\xd4\xa4Fl\\ovn\x85\x96\xcc\xbf\x13N\\\xa1c\xf9\rG\x1e\x12wO7"),
    ]
)
def test_hash_algorithm(plain_password, algorithm_fn, iterations, salt, expected_result):
    service = PasswordService()
    assert service.get_hash(
        plain_password=plain_password,
        algorithm_fn=algorithm_fn,
        iterations=iterations,
        salt=salt
    ) == expected_result


@pytest.mark.parametrize(
    "plain_password, algorithm, iterations, salt, expected_result", [
        ("test_password", PasswordAlgorithms.PLAIN,
         1, b"salt", "plain$1$dGVzdF9wYXNzd29yZA==$c2FsdA=="),
        ("test_password", PasswordAlgorithms.SHA256,
         1, b"salt", "sha256$1$QhxwnckONM27GtQuOUuT4dIo0+aGy47BbeWb/q87mNY=$c2FsdA=="),
        ("test_password", PasswordAlgorithms.SHA256,
         1000, b"salt", "sha256$1000$svPTalE5SNSkRmxcb3ZuhZbMvxNOXKFj+Q1HHhJ3Tzc=$c2FsdA==")
    ])
def test_hash_password(plain_password, algorithm, iterations, salt, expected_result):
    service = PasswordService()
    hashed_password = service.hash_password(
        plain_password=plain_password,
        algorithm=algorithm,
        iterations=iterations,
        salt=salt
    )
    assert hashed_password == expected_result


@pytest.mark.parametrize(
    "plain_password, password, expected_result", [
        ("test_password", "plain$1$dGVzdF9wYXNzd29yZA==$c2FsdA==", True),
        ("test_password_wrong", "plain$1$dGVzdF9wYXNzd29yZA==$c2FsdA==", False),
        ("test_password", "sha256$1$QhxwnckONM27GtQuOUuT4dIo0+aGy47BbeWb/q87mNY=$c2FsdA==", True),
        ("test_password_wrong", "sha256$1$QhxwnckONM27GtQuOUuT4dIo0+aGy47BbeWb/q87mNY=$c2FsdA==", False),
    ])
def test_check_password(plain_password, password, expected_result):
    service = PasswordService()
    assert service.check_password(plain_password=plain_password, password=password) == expected_result


@pytest.mark.parametrize(
    "test_input", [
        "password123456"])
def test_validate_min_length_success(test_input: str, password_min_length_env):
    assert len(test_input) >= CORRECT_PASSWORD_MIN_LENGTH
    assert validate_min_length(test_input)


@pytest.mark.parametrize(
    "test_input", [
        "password1"])
def test_validate_min_length_value_error(test_input: str, password_min_length_env):
    assert len(test_input) < CORRECT_PASSWORD_MIN_LENGTH
    with pytest.raises(PasswordValidationError):
        validate_min_length(test_input)


@pytest.mark.parametrize(
    "test_input", [
        "password123456"])
def test_validate_max_length_success(test_input: str, password_max_length_env):
    assert len(test_input) < CORRECT_PASSWORD_MAX_LENGTH
    assert validate_max_length(test_input)


@pytest.mark.parametrize(
    "test_input", [
        "password_too_long_too_long_too_long"])
def test_validate_max_length_value_error(test_input: str, password_max_length_env):
    assert len(test_input) > CORRECT_PASSWORD_MAX_LENGTH
    with pytest.raises(PasswordValidationError):
        validate_max_length(test_input)
