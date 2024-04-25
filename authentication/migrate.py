from argparse import ArgumentParser
from enum import Enum

from config import get_test_database_url, ADAPTERS
from migrations.operations import migrate_head, migration_autogenerate


class Operations(str, Enum):
    HEAD = "head"
    AUTOGENERATE = "autogenerate"


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "operation",
        type=Operations,
        choices=list(Operations)
    )
    operations = {
        Operations.HEAD: migrate_head,
        Operations.AUTOGENERATE: migration_autogenerate
    }

    args = parser.parse_args()
    operation = operations[args.operation]

    database_url = get_test_database_url(ADAPTERS.SYNC)

    operation(database_url)
