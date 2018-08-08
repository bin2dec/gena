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

    def __setattr__(self, key: str, value: Any) -> None:
        if key == 'data':
            super().__setattr__(key, value)
        else:
            self.data[key] = value


context = Context()
