from __future__ import annotations

from typing import Any

from gena.utils import UserDict


__all__ = (
    'context',
)


class Context(UserDict):
    def add_item(self, key: str, value: Any = None, *, replace: bool = False) -> Any:
        if replace or key not in self.data:
            self.data[key] = value
        return self.data[key]


context = Context()
