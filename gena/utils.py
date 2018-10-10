from __future__ import annotations

import importlib.util
import os

from datetime import datetime
from types import ModuleType
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


def import_attr(attr: str) -> Any:
    """Import a module attribute. For example:

    import gena.utils
    runner = gena.utils.import_attr('gena.runners.FileRunner')

    It returns the FileRunner object from the gena.runners module.
    """

    module_name, attr_name = attr.strip().rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


def import_module(path: str) -> ModuleType:
    """Import a module. For example:

    import gena.utils
    user_settings = gena.utils.import_module('/home/user/settings.py')
    """

    name = os.path.basename(path)
    if not name:
        raise ImportError(f'cannot import "{path}"')
    name = os.path.splitext(name)[0]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def map_as_kwargs(m):
    return ', '.join(f'{k}={v!r}' for k, v in m.items())
