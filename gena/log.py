import logging

from gena.settings import settings


NORMAL_LOG_FORMAT = '{levelname:10}{message}'

VERBOSE_LOG_FORMAT = '{asctime:25}{levelname:10}{message}  ({name}:{lineno})'


def config(level=None, *, name=None, handler=None):
    """Configure logger `name`."""

    if handler is None:
        fmt = VERBOSE_LOG_FORMAT if level == logging.DEBUG else NORMAL_LOG_FORMAT
        formatter = logging.Formatter(fmt, style='{')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

    logger = logging.getLogger(name)  # if `name` is None, then the root logger is returned
    logger.addHandler(handler)
    if level is None:
        level = logging.DEBUG if settings.DEBUG else logging.WARNING
    logger.setLevel(level)
