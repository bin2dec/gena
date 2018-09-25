from __future__ import annotations

from collections import UserDict
from typing import Any


__all__ = (
    'context',
)


class Context(UserDict):
    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self.data[name]
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'data':
            super().__setattr__(name, value)
        else:
            self.data[name] = value

    def add_item(self, key: str, value: Any = None, *, replace: bool = False) -> Any:
        if replace or key not in self.data:
            self.data[key] = value
        return self.data[key]


context = Context()
