from __future__ import annotations

import logging
import os
import shutil

from abc import ABC, abstractmethod
from collections import UserDict, UserList
from enum import Enum
from typing import Any, Iterable, Iterator, Union

from gena import utils


__all__ = (
    'binary_file',
    'File',
    'FileLike',
    'FileMeta',
    'FileMetaValue',
    'FilePath',
    'FilePathLike',
    'FileType',
    'text_file',
)


logger = logging.getLogger(__name__)


AnyPath = Union[os.PathLike, str]
FileContents = Union[None, bytes, str]


class FileType(Enum):
    BINARY = 'b'
    TEXT = 't'


class FileMetaValue(UserList):
    linesep = os.linesep

    def __str__(self, *args, **kwargs) -> str:
        return self.linesep.join(str(_) for _ in self.data)


class FileMeta(UserDict):
    def __setitem__(self, key: str, value: Iterable) -> None:
        self.data[key] = FileMetaValue(value)

    def __getattr__(self, name: str) -> Iterable:
        if name in self:
            return self.data[name]
        raise AttributeError(name)


class FilePathLike(os.PathLike):
    @property
    @abstractmethod
    def basename(self) -> str:
        pass

    @basename.setter
    @abstractmethod
    def basename(self, basename: AnyPath) -> None:
        pass

    @property
    @abstractmethod
    def directory(self) -> str:
        pass

    @directory.setter
    @abstractmethod
    def directory(self, directory: AnyPath) -> None:
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        pass

    @extension.setter
    @abstractmethod
    def extension(self, extension: AnyPath) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @name.setter
    @abstractmethod
    def name(self, name: AnyPath) -> None:
        pass

    @property
    @abstractmethod
    def path(self) -> str:
        pass

    @path.setter
    @abstractmethod
    def path(self, path: AnyPath) -> None:
        pass

    @abstractmethod
    def copy(self) -> FilePathLike:
        pass


class FilePath(FilePathLike):
    def __init__(self, path: AnyPath, *paths: AnyPath) -> None:
        self.join(path, *paths)  # init self._path

    def __add__(self, other: AnyPath) -> FilePath:
        return self.__class__(self._path, other)

    def __bytes__(self):
        return os.fsencode(self._path)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FilePath):
            return os.path.realpath(self) == os.path.realpath(other)
        return False

    def __fspath__(self) -> str:
        return self._path

    def __iadd__(self, other: AnyPath) -> FilePath:
        self.join(self._path, other)
        return self

    def __iter__(self) -> Iterator[str]:
        return iter(self._path)

    def __radd__(self, other: AnyPath) -> FilePath:
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
    def basename(self, basename: AnyPath) -> None:
        basename = utils.fspath(basename)
        if os.sep in basename:
            raise ValueError('separators are not allowed in a file base name')
        self.join(self.directory, f'{basename}{self.extension}')

    @property
    def directory(self) -> str:
        """Return the file directory.

        For example:
        if path == /usr/share/fish/config.fish, then directory == /usr/share/fish.
        """

        return os.path.dirname(self._path)

    @directory.setter
    def directory(self, directory: AnyPath) -> None:
        self.join(directory, self.name)

    @property
    def extension(self) -> str:
        """Return the file extension (with a dot prefix).

        For example:
        if path == /usr/share/fish/config.fish, then extension == .fish.
        """

        return os.path.splitext(self.name)[1]

    @extension.setter
    def extension(self, extension: AnyPath) -> None:
        extension = utils.fspath(extension)
        if os.sep in extension:
            raise ValueError('separators are not allowed in a file extension')
        if extension.startswith('.'):
            name = f'{self.basename}{extension}'
        else:
            name = f'{self.basename}.{extension}'
        self.join(self.directory, name)

    @property
    def name(self) -> str:
        """Return the file name with its extension.

        For example:
        if path == /usr/share/fish/config.fish, then basename == config.fish.
        """

        return os.path.basename(self._path)

    @name.setter
    def name(self, name: AnyPath) -> None:
        name = utils.fspath(name)
        if os.sep in name:
            raise ValueError('separators are not allowed in a file name')
        self.join(self.directory, name)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: AnyPath) -> None:
        self.join(path)

    def copy(self) -> FilePath:
        return self.__class__(self)

    def join(self, *paths: AnyPath) -> None:
        """Join one or more path components and assign the result to self._path."""
        path = os.path.join(*paths) if paths else ''
        if isinstance(path, bytes):
            path = os.fsdecode(path)
        self._path: str = os.path.normpath(path)


class FileLike(ABC):
    @property
    @abstractmethod
    def contents(self) -> FileContents:
        pass

    @contents.setter
    @abstractmethod
    def contents(self, contents: FileContents) -> None:
        pass

    @property
    @abstractmethod
    def meta(self) -> FileMeta:
        pass

    @property
    @abstractmethod
    def path(self) -> FilePathLike:
        pass

    @property
    @abstractmethod
    def type(self) -> FileType:
        pass

    @type.setter
    @abstractmethod
    def type(self, type_: FileType) -> None:
        pass

    @abstractmethod
    def is_binary(self) -> bool:
        pass

    @abstractmethod
    def is_text(self) -> bool:
        pass

    @abstractmethod
    def save(self, append=False) -> bool:
        pass


class File(FileLike):
    encoding = 'utf-8'

    def __init__(self, path: AnyPath, *paths: AnyPath, **kwargs) -> None:
        self._path = FilePath(path, *paths)
        self._opath = self._path.copy()
        self._contents: FileContents = None
        self._meta = FileMeta()
        self._type = kwargs.pop('type', FileType.TEXT)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self, *args, **kwargs):
        return f'{self.__class__.__name__}({self._path.path!r}, type={self._type})'

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
            encoding = self.encoding if self.is_text() else None
            with open(self._opath.path, f'r{self._type.value}', encoding=encoding) as file:
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

    @property
    def type(self) -> FileType:
        return self._type

    @type.setter
    def type(self, type_: FileType) -> None:
        if self._type is not type_:
            if self._contents is not None:
                if type_ is FileType.BINARY and isinstance(self._contents, str):
                    self._contents = self._contents.encode(encoding=self.encoding)  # str -> bytes
                elif type_ is FileType.TEXT and isinstance(self._contents, bytes):
                    self._contents = self._contents.decode(encoding=self.encoding)  # bytes -> str
                else:
                    raise TypeError('unknown or not acceptable type')
            self._type = type_

    def is_binary(self) -> bool:
        return self._type is FileType.BINARY

    def is_text(self) -> bool:
        return self._type is FileType.TEXT

    def save(self, append=False) -> bool:
        """Save the file.

        If `append` is False and the file contents aren't changed, it's a simple copy of the original file.
        If `append` is True and there's already a file with the same name, then the contents are appended to
        the end of this existing file.

        Note that it's not possible to rewrite the original file using this method.
        """

        if os.path.exists(self._opath) and self._path == self._opath:
            return False

        if os.path.exists(self._path):
            if not append:
                logger.warning('"%s" already exists and will be replaced', self._path)
        elif self._path.directory and not os.path.exists(self._path.directory):
            os.makedirs(self._path.directory)

        if append or self._contents is not None:
            mode = 'a' if append else 'w'
            mode += self._type.value  # can be 'at', 'ab', 'wt', or 'wb'
            encoding = self.encoding if self.is_text() else None
            with open(self._path, mode, encoding=encoding) as file:
                file.write(self.contents)
            self._contents = None
        else:
            shutil.copy(self._opath.path, self._path.path)

        self._opath = self._path.copy()

        logger.info('Saved "%s"', self.path.path)

        return True


def binary_file(*args, **kwargs) -> File:
    """Factory for creating binary files."""
    kwargs['type'] = FileType.BINARY
    return File(*args, **kwargs)


def text_file(*args, **kwargs) -> File:
    """Factory for creating text files."""
    kwargs['type'] = FileType.TEXT
    return File(*args, **kwargs)
