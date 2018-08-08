from __future__ import annotations

import os
import shutil

from collections import UserDict, UserList
from enum import Enum
from typing import Any, Iterable, Iterator, Union

from gena import utils


__all__ = (
    'File',
    'FileMeta',
    'FilePath',
    'FileType',
)


FileContents = Union[None, bytes, str]
PathLike = Union[os.PathLike, str]


def join_paths(*paths: PathLike) -> str:
    """Join one or more path components. The result's type is always str."""
    path = os.path.join(*paths) if paths else ''
    if isinstance(path, bytes):
        return os.fsdecode(path)
    return path


class FileType(Enum):
    BINARY = 'b'
    TEXT = 't'


class FileMetaValue(UserList):
    linesep = os.linesep

    def __str__(self, *args, **kwargs) -> str:
        return self.linesep.join(str(_) for _ in self.data)


class FileMeta(UserDict):
    def __setitem__(self, key: str, item: Iterable) -> None:
        self.data[key] = FileMetaValue(item)

    def __getattr__(self, name: str) -> Iterable:
        if name in self:
            return self.data[name]
        raise AttributeError(name)


class FilePath(os.PathLike):
    def __init__(self, path: PathLike, *paths: PathLike) -> None:
        self._path = join_paths(path, *paths)

    def __add__(self, other: PathLike) -> FilePath:
        return self.__class__(self._path, other)

    def __bytes__(self):
        return os.fsencode(self._path)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FilePath):
            return os.path.realpath(self) == os.path.realpath(other)
        return False

    def __fspath__(self) -> str:
        return self._path

    def __iadd__(self, other: PathLike) -> FilePath:
        self._path = join_paths(self._path, other)
        return self

    def __iter__(self) -> Iterator[str]:
        return iter(self._path)

    def __radd__(self, other: PathLike) -> FilePath:
        return self.__class__(other, self._path)

    def __repr__(self, *args, **kwargs):
        return f'{self.__class__.__name__}({self._path!r})'

    def __str__(self, *args, **kwargs) -> str:
        return self._path

    @property
    def basename(self) -> str:
        """Return the file name without its extension.

        For example:
        if path == /usr/share/fish/config.fish, then basename == config.
        """

        return os.path.splitext(self.name)[0]

    @basename.setter
    def basename(self, basename: str) -> None:
        basename = utils.fspath(basename)
        if os.sep in basename:
            raise ValueError('separators are not allowed in a file base name')
        self._path = join_paths(self.directory, f'{basename}{self.extension}')

    @property
    def directory(self) -> str:
        """Return the file directory.

        For example:
        if path == /usr/share/fish/config.fish, then directory == /usr/share/fish.
        """

        return os.path.dirname(self._path)

    @directory.setter
    def directory(self, directory: str) -> None:
        self._path = join_paths(directory, self.name)

    @property
    def extension(self) -> str:
        """Return the file extension (with a dot prefix).

        For example:
        if path == /usr/share/fish/config.fish, then extension == .fish.
        """

        return os.path.splitext(self.name)[1]

    @extension.setter
    def extension(self, extension: str) -> None:
        extension = utils.fspath(extension)
        if os.sep in extension:
            raise ValueError('separators are not allowed in a file extension')
        if extension.startswith('.'):
            name = f'{self.basename}{extension}'
        else:
            name = f'{self.basename}.{extension}'
        self._path = join_paths(self.directory, name)

    @property
    def name(self) -> str:
        """Return the file name with its extension.

        For example:
        if path == /usr/share/fish/config.fish, then basename == config.fish.
        """

        return os.path.basename(self._path)

    @name.setter
    def name(self, name: str) -> None:
        name = utils.fspath(name)
        if os.sep in name:
            raise ValueError('separators are not allowed in a file name')
        self._path = join_paths(self.directory, name)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        self._path = join_paths(path)

    def copy(self) -> FilePath:
        return self.__class__(self)


class File:
    _contents: FileContents = None

    def __init__(self, path: PathLike, *paths: PathLike, file_type: FileType = FileType.TEXT) -> None:
        self._path = FilePath(path, *paths)
        self._opath = self._path.copy()
        self._type = file_type
        self._meta = FileMeta()

    def __repr__(self, *args, **kwargs):
        return f'{self.__class__.__name__}({self._path.path!r}, file_type={self._type})'

    def __str__(self, *args, **kwargs) -> str:
        return self._path.path

    @property
    def atime(self) -> int:
        return int(os.stat(self._opath.path).st_atime)

    @property
    def ctime(self) -> int:
        return int(os.stat(self._opath.path).st_ctime)

    @property
    def contents(self) -> FileContents:
        if self._contents is None:
            with open(self._opath.path, f'r{self._type.value}') as file:
                self._contents = file.read()
        return self._contents

    @contents.setter
    def contents(self, contents: FileContents) -> None:
        if self._type is FileType.TEXT:
            if not isinstance(contents, str):
                raise TypeError('contents must be str for text files')
        elif not isinstance(contents, bytes):
            raise TypeError('contents must be bytes for binary files')
        self._contents = contents

    @property
    def meta(self) -> FileMeta:
        return self._meta

    @property
    def mtime(self) -> int:
        return int(os.stat(self._opath.path).st_mtime)

    @property
    def path(self) -> FilePath:
        return self._path

    def is_binary(self) -> bool:
        return self._type is FileType.BINARY

    def is_text(self) -> bool:
        return self._type is FileType.TEXT

    def save(self) -> bool:
        """Commit changes by creating a new file.

        It's not possible to rewrite an old file, you can only create a new one.
        If file contents aren't changed, it will be a simple copy.
        """

        if self._path == self._opath:
            return False

        if self._path.directory and not os.path.exists(self._path.directory):
            os.makedirs(self._path.directory)

        if self._contents is not None:
            with open(self._path, f'w{self._type.value}') as file:
                file.write(self._contents)
            self._contents = None
        else:
            shutil.copy(self._opath.path, self._path.path)

        self._opath = self._path.copy()

        return True
