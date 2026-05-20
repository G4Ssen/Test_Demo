import logging
import sys


_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%dT%H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=_FORMAT,
    datefmt=_DATE_FMT,
    stream=sys.stdout,
)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with the project-wide format."""
    logger = logging.getLogger(name)
    return logger
