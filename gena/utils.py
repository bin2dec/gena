import os

from datetime import datetime
from dateutil.parser import parse as timestrparse
from importlib import import_module


__all__ = (
    'fspath',
    'get_datetime',
    'import_attr',
)


def fspath(path):
    new_path = os.fspath(path)
    if isinstance(new_path, bytes):
        return os.fsdecode(new_path)
    return new_path


def get_datetime(s, *args, **kwargs):
    if isinstance(s, datetime):
        return s
    try:
        return datetime.fromtimestamp(s)
    except TypeError:
        return timestrparse(s, *args, **kwargs)


def import_attr(s, default=None):
    module_name, attr = s.strip().rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, attr, default)
