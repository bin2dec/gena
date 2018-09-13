from __future__ import annotations

import os

from datetime import datetime
from importlib import import_module
from typing import Any

from dateutil.parser import parse as timestrparse


__all__ = (
    'fspath',
    'get_datetime',
    'import_attr',
    'map_as_kwargs',
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


def import_attr(path: str) -> Any:
    """Import a module attribute. For example:

    runner = utils.import_attr('gena.runners.FileRunner')
    """

    module_name, attr = path.strip().rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, attr)


def map_as_kwargs(m):
    return ', '.join(f'{k}={v!r}' for k, v in m.items())
