import os
import re
from datetime import timedelta

from exceptions import EnvironmentValueError

DOMAIN_REGEX = r"^(((?!-))(xn--|_)?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?" \
               r"([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$"

PORT_REGEX = r"^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]" \
             r"{2}|655[0-2][0-9]|6553[0-5])$"


# App
def get_app_secret() -> str:
    """SECRET_KEY should be from 12 to 36 long and can contain any printable symbol"""
    regex = r"^[\x20-\x7E]{12,36}$"
    key = "APP_SECRET_KEY"
    value = os.getenv(key, "")

    if not re.compile(regex).match(value):
        raise EnvironmentValueError(key)

    return value


# Passwords
def get_password_min_length() -> int:
    key = "PASSWORD_MIN_LENGTH"
    value = os.getenv(key)
    if not value:
        value = os.getenv(key, "8")

    try:
        return int(value)
    except ValueError:
        raise EnvironmentValueError(key)


def get_password_max_length() -> int:
    key = "PASSWORD_MAX_LENGTH"
    value = os.getenv(key, "16")

    try:
        return int(value)
    except ValueError:
        raise EnvironmentValueError(key)


def get_password_iterations() -> int:
    key = "PASSWORD_ITERATIONS"
    value = os.getenv(key, "300000")
    try:
        numeric_value = int(value)

    except ValueError:
        raise EnvironmentValueError(key)

    if numeric_value > 1e6:
        raise EnvironmentValueError(key)
    return numeric_value


# PostgreSQL
def get_postgres_host() -> str:
    """Should contain a valid domain"""
    key = "POSTGRES_HOST"
    value = os.getenv(key, "127.0.0.1")
    #
    # if not re.compile(DOMAIN_REGEX).match(value):
    #     raise EnvironmentValueError(key)

    return value


def get_postgres_port() -> str:
    """Should contain a valid port"""
    key = "POSTGRES_PORT"
    value = os.getenv(key, "5432")

    if not re.compile(PORT_REGEX):
        raise EnvironmentValueError(key)

    return value


def get_postgres_db() -> str:
    """Should contain postgres database name"""
    key = "POSTGRES_DB"
    value = os.getenv(key)

    if not value:
        raise EnvironmentValueError(key)

    return value


def get_postgres_user() -> str:
    """Should contain postgres user that can access the postgres database"""
    key = "POSTGRES_USER"
    value = os.getenv(key)

    if not value:
        raise EnvironmentValueError(key)

    return value


def get_postgres_password() -> str:
    """Should contain postgres password that is used to access the postgres database"""
    key = "POSTGRES_PASSWORD"
    value = os.getenv(key)

    if not value:
        raise EnvironmentValueError(key)

    return value


def get_frontend_url() -> str:
    key = "FRONTEND_URL"
    value = os.getenv(key)

    if not value:
        raise EnvironmentValueError(key)

    return value


def get_authentication_code_valid_minutes() -> int:
    key = "AUTHENTICATION_CODE_VALID_MINUTES"
    value = os.getenv(key, "5")

    try:
        value = int(value)
    except ValueError:
        raise EnvironmentValueError(key)

    return value


def get_access_token_valid() -> timedelta:
    key = "ACCESS_TOKEN_VALID_MINUTES"
    value = os.getenv(key, "30")

    try:
        value = int(value)
    except ValueError:
        raise EnvironmentValueError(key)

    return timedelta(minutes=value)


def get_refresh_token_valid() -> timedelta:
    key = "REFRESH_TOKEN_VALID_DAYS"
    value = os.getenv(key, "356")

    try:
        value = int(value)
    except ValueError:
        raise EnvironmentValueError(key)

    return timedelta(days=value)
