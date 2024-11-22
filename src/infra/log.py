import logging
import sys

formatter = logging.Formatter(
    fmt="%(levelname)s | %(asctime)s | %(process)d | %(threadName)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)


def setup_logging(log_level=logging.INFO):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    root_logger.handlers.clear()

    root_logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
    return logger
