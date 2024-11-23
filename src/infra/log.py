import logging

import sys


def setup_logging(log_level=logging.INFO):
    """
    Reconfigure logging explicitly to avoid suppression in async contexts.
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logging.getLogger()
