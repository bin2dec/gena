from __future__ import annotations

from typing import Any

from gena.utils import UserDict


__all__ = (
    'context',
)


class Context(UserDict):
    def add(self, key: str, value: Any = None, *, replace: bool = False) -> Any:
        if replace or key not in self.data:
            self.data[key] = value
        return self.data[key]

    def add_to_list(self, key: str, value: Any) -> None:
        if key in self.data:
            self.data[key].append(value)
        else:
            self.data[key] = [value]


context = Context()
