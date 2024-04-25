import os

from alembic import command
from alembic.config import Config

from config import get_alembic_config_location, get_root_dir


def get_alembic_config(database_url: str) -> Config:
    config = Config(get_alembic_config_location())
    config.set_main_option(
        "sqlalchemy.url", database_url)
    config.set_main_option(
        "script_location", os.path.join(get_root_dir(), "migrations"))

    return config


def migrate_head(database_url: str):
    alembic_config = get_alembic_config(database_url)
    command.upgrade(alembic_config, "head")


def migration_autogenerate(database_url: str):
    alembic_config = get_alembic_config(database_url)
    command.revision(alembic_config, autogenerate=True)
