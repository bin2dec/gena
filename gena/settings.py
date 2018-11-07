import os

from importlib import import_module
from inspect import getmembers

from gena import default_settings
from gena import utils
from gena.utils import UserDict


__all__ = (
    'settings',
)


def _get_members(obj):
    """Grab all uppercase attributes from the object `obj`."""
    return {k: v for k, v in getmembers(obj) if k.isupper()}


class Settings(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {**_get_members(default_settings), **self.data}

    def __str__(self):
        return os.linesep.join(f'{k} = {v!r}' for k, v in self.data.items())

    def clear(self):
        """Return to the default settings."""
        super().clear()
        self.data = _get_members(default_settings)

    def load_from_file(self, path):
        """Load settings from a file. For example:

        from gena import settings
        settings.load_from_file('/home/user/settings.py')
        """

        module = utils.import_module(path)
        self.data.update(_get_members(module))

    def load_from_module(self, module):
        """Load settings from a module. For example:

        from gena import settings
        settings.load_from_module('gena.contrib.blog.settings')
        """

        module = import_module(module)
        self.data.update(_get_members(module))


settings = Settings()
