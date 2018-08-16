import importlib.util
import os

from collections import UserDict
from inspect import getmembers
from types import ModuleType

from gena import global_settings


__all__ = (
    'settings',
)


def import_module(path):
    name = os.path.basename(path)
    if not name:
        raise ImportError(f'cannot import "{path}"')
    name = os.path.splitext(name)[0]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Settings(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_settings = {k: v for k, v in getmembers(global_settings) if k.isupper()}
        self.data = {**default_settings, **self.data}

    def __getattr__(self, name):
        if name in self:
            return self.data[name]
        raise AttributeError(name)

    def __setattr__(self, key, value):
        if key == 'data':
            super().__setattr__(key, value)
        else:
            self.data[key] = value

    def clear(self):
        super().clear()
        self.data = {k: v for k, v in getmembers(global_settings) if k.isupper()}

    def load_from_module(self, module):
        if not isinstance(module, ModuleType):
            module = import_module(module)
        self.data.update((k, v) for k, v in getmembers(module) if k.isupper())


settings = Settings()
