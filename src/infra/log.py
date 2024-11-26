import logging

import sys
from logging import Logger


def setup_logging(log_level: int | str = logging.INFO) -> Logger:
    """
    Reconfigure logging explicitly to avoid suppression in async contexts.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logging.getLogger()
