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


context = Context()
