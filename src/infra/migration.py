import logging

from alembic.config import Config
from alembic import command


def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logging.info("Migrations completed successfully")
    except Exception as e:
        logging.error(f"Migration failed: {e}", exc_info=True)
        raise
