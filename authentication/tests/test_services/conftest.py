import os

import pytest

CORRECT_PASSWORD_MIN_LENGTH = 12
CORRECT_PASSWORD_MAX_LENGTH = 24


@pytest.fixture
def password_min_length_env():
    key = "PASSWORD_MIN_LENGTH"
    initial_value = os.getenv(key)
    os.environ[key] = str(CORRECT_PASSWORD_MIN_LENGTH)

    yield CORRECT_PASSWORD_MIN_LENGTH

    if initial_value is None:
        os.environ.pop(key)
    else:
        os.environ[key] = initial_value


@pytest.fixture
def password_max_length_env():
    key = "PASSWORD_MAX_LENGTH"
    initial_value = os.getenv(key)
    os.environ[key] = str(CORRECT_PASSWORD_MAX_LENGTH)

    yield

    if initial_value is None:
        os.environ.pop(key)
    else:
        os.environ[key] = initial_value
