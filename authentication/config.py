import os
from enum import Enum

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from env import get_password_iterations as get_password_iterations_env
from env import get_postgres_host, get_postgres_db, \
    get_postgres_user, get_postgres_password, get_postgres_port
from services.password_service.validators import validate_min_length, validate_max_length


class ADAPTERS(str, Enum):
    ASYNC = "postgresql+asyncpg"
    SYNC = "postgresql+psycopg2"


APP_NAME = "metadata_service"


def get_root_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_test_database_url(adapter: ADAPTERS) -> str:
    return f"{adapter}" \
           f"://{get_postgres_user()}:{get_postgres_password()}" \
           f"@{get_postgres_host()}:{get_postgres_port()}" \
           f"/{get_postgres_db()}"


def get_alembic_config_location():
    return os.path.join(get_root_dir(), "alembic.ini")


def get_password_validators():
    validators = []

    if os.environ.get("PASSWORD_MIN_LENGTH"):
        validators.append(validate_min_length)

    if os.environ.get("PASSWORD_MAX_LENGTH"):
        validators.append(validate_max_length)

    return validators


def get_password_algorithm():
    from services.password_service.service import PasswordAlgorithms
    return PasswordAlgorithms.SHA256


def get_password_iterations():
    return get_password_iterations_env()


db_engine = None


def get_session() -> AsyncSession:
    global db_engine
    if not db_engine:
        db_engine = create_async_engine(
            get_test_database_url(ADAPTERS.ASYNC),
            poolclass=AsyncAdaptedQueuePool,
        )

    return AsyncSession(db_engine, expire_on_commit=False)
