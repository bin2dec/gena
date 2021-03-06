from __future__ import annotations

import gzip
import logging
import os
import subprocess

from abc import ABC, abstractmethod
from sys import stdout
from typing import Callable, Iterable, Optional, Sequence, TypeVar, Union

from markdown import Markdown

from gena.context import context
from gena.files import FileLike, FileType
from gena.settings import settings
from gena.templating import JinjaTemplateEngine, TemplateEngine
from gena.utils import map_as_kwargs


__all__ = (
    'BinaryProcessor',
    'BundleProcessor',
    'ExternalProcessor',
    'FileMetaProcessor',
    'FileNameProcessor',
    'GroupProcessor',
    'GunzipProcessor',
    'GzipProcessor',
    'MarkdownProcessor',
    'Processor',
    'SavingProcessor',
    'StdoutProcessor',
    'TemplateProcessor',
    'TextProcessor',
    'TypeProcessor',
)


logger = logging.getLogger(__name__)


T = TypeVar('T')
FileCallable = Union[T, Callable[[FileLike], T]]


class Processor(ABC):
    """Abstract base class for all processors."""

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def process(self, file: FileLike) -> FileLike:
        if logger.isEnabledFor(logging.DEBUG):
            attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
            logger.debug('%s(%s) is processing %r', self.__class__.__name__, map_as_kwargs(attrs), file)
        return file


class BinaryProcessor(Processor):
    """Base class for all processors that work with binary files (when file contents are bytes)."""

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        if not file.is_binary():
            raise TypeError(f'{self.__class__.__name__} supports binary files only')
        return file


class TextProcessor(Processor):
    """Base class for all processors that work with text files (when file contents are a string)."""

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        if not file.is_text():
            raise TypeError(f'{self.__class__.__name__} supports text files only')
        return file


class BundleProcessor(Processor):
    """Bundle the file contents up.

    It can be useful in situations when you need to include several files in another one
    (for example, to inline all your CSS files in the index page).

    An example:

    1) In your settings file:
    ...
    RULES = (
        {
            'test': '*.css',
            'processors': (
                {
                    'processor': 'gena.processors.BundleProcessor',
                    'options': {
                        'name': 'css',
                    },
                },
            ),
            'priority': 10,  # set a higher priority for css files (a lower number means a higher priority)
        },
        {
            'test': '*.md',
            'processors': (
                {'processor': 'gena.processors.MarkdownProcessor'},
                {
                    'processor': 'gena.processors.TemplateProcessor',
                    'options': {
                        'template': 'template.html',
                    },
                },
                {'processor': 'gena.processors.StdoutProcessor'},
            ),
            'priority': 20,
        },
    )
    ...

    2) In template.html:
    ...
    <head>
        ...
        <style>{{ context.css }}</style>
        ...
    </head>
    ...

    Notice that all bundled files must be the same type (binary or text).
    """

    def __init__(self, *, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        try:
            context[self.name] += file.contents
        except KeyError:
            context[self.name] = file.contents
        return file


class ExternalProcessor(Processor):
    """Run an external command.

    The file contents are sent to stdin of the process. Then captured stdout is assigned back to the file contents.
    For example, we would like to compress our JavaScript files that aren't compressed yet:

    RULES = (
        ...
        {
            'test': '*[!.min].js',
            'processors': (
                ...
                {
                    'processor': 'gena.processors.ExternalProcessor',
                    'options': {
                        'command': ['uglifyjs'],
                    },
                },
                ...
                {
                    'processor': 'gena.processors.FileNameProcessor',
                    'options': {
                        'name': '{file.path.basename}.min.js',
                    },
                },
                ...
            ),
        },
        ...
    )

    Here we used third-party minifier called UglifyJS (http://lisperator.net/uglifyjs/) to compress these files.
    """

    def __init__(self, *, command: Sequence[str], chdir: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.command = command
        self.chdir = chdir

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        curdir = os.getcwd()
        if self.chdir is None:
            os.chdir(file.path.directory)
        else:
            os.chdir(self.chdir)
        output = subprocess.run(self.command,
                                input=file.contents,
                                shell=False,
                                stdout=subprocess.PIPE,
                                text=file.is_text() or None,
                                **settings.EXTERNAL_PROCESSOR)
        os.chdir(curdir)
        file.contents = output.stdout
        return file


class FileMetaProcessor(Processor):
    """Run an arbitrary function against a meta value.

    The first argument of the callback function is always a meta value.
    Both the meta value and the function result must be iterable objects (like files.FileMetaValue).
    The default value is used when the required one doesn't exist. It must also be either an iterable object or
    some callable which returns an iterable object.
    For example, we would like to make a slug from our article title for future use:

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {
                    'processor': 'gena.processors.FileMetaProcessor',
                    'options': {
                        'key': 'slug',
                        'callback': slugify,
                        'default': lambda file: file.meta.title,
                        'skip_if_exists': True,
                    },
                }
                ...
            ),
        },
        ...
    )

    Here we suppose that the slug field might not exist at all, and thus we declared the default value
    (file.meta.title). The callback function (slugify) will run against this default value.
    If the slug field already exists, then no processing will be done.
    """

    def __init__(self, *, key: str, callback: Callable, callback_args=None, callback_kwargs=None,
                 default: Optional[FileCallable[Iterable]] = None, skip_if_exists: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)

        self.key = key
        self.callback = callback
        self.callback_args = callback_args or ()
        self.callback_kwargs = callback_kwargs or {}
        self.default = default
        self.skip_if_exists = skip_if_exists

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)

        if self.key in file.meta and self.skip_if_exists:
            return file

        default = self.default(file) if callable(self.default) else self.default
        values = file.meta.get(self.key, default)
        if values is not None:
            new_values = []
            for value in values:
                new_value = self.callback(value, *self.callback_args, **self.callback_kwargs)
                new_values.append(new_value)
            file.meta[self.key] = new_values
            logger.debug('Added meta values to %r: %s=%r', file, self.key, file.meta[self.key])

        return file


class FileNameProcessor(Processor):
    """Change the file name (base name + extension).

    For example, we would like to change extensions of our markdown files (presumably after some markdown processing):

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {
                    'processor': 'gena.processors.FileNameProcessor',
                    'options': {
                        'name': '{file.basename}.html',
                    },
                },
                ...
            ),
        },
        ...
    )

    The name argument must be a string or a callable which returns a string.
    """

    def __init__(self, *, name: FileCallable[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        old_name = file.path.name
        if callable(self.name):
            file.path.name = self.name(file)
        else:
            file.path.name = self.name.format(file=file)
        logger.debug('Renamed %r: "%s" to "%s"', file, old_name, file.path.name)
        return file


class GroupProcessor(Processor):
    """Create groups of files.

    It can be useful in many cases for the final jobs like a job of generation of index file with, for instance, links
    to your articles.
    Let's look at the following rule:

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {
                    'processor': 'gena.processors.GroupProcessor',
                    'options': {
                        'name': 'articles',
                    },
                },
                ...
            ),
        },
        ...
    )

    According to this rule, all our markdown files will be part of the group named `articles` (now globally accessible
    via context.articles).
    Next, we can use this bunch of the files in some final job to generate an article list.
    Note that it's generally better to place GroupProcessor after SavingProcessor.
    """

    def __init__(self, *, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        context.add_to_list(self.name, file)
        return file


class GunzipProcessor(BinaryProcessor):
    """Decompress the file contents."""

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.contents = gzip.decompress(file.contents)
        return file


class GzipProcessor(BinaryProcessor):
    """Compress the file contents."""

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.contents = gzip.compress(file.contents, compresslevel=settings.GZIP_COMPRESS_LEVEL)
        return file


class MarkdownProcessor(TextProcessor):
    """Convert Markdown syntax into HTML.

    For example, we would like to convert all our markdown files:

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {'processor': 'gena.processors.MarkdownProcessor'},
                ...
            ),
        },
        ...
    )

    Notice that this processor only changes the file contents, but it doesn't rename the file.
    If you need to do that, you should use another processor (e.g. FileNameProcessor).

    You can also use some additional processing arguments and plugins. In order to do that, just add
    MARKDOWN_OPTIONS to your settings file.
    """

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        md = Markdown(**settings.MARKDOWN_OPTIONS)
        file.contents = md.convert(file.contents)
        meta = getattr(md, 'Meta', {})
        file.meta.update(meta)
        return file


class SavingProcessor(Processor):
    """Save the file.

    If `append` is True and there's already a file with the same name, then the contents are appended to
    the end of this existing file.

    A simple usage example:

    RULES = (
        ...
        {
            'test': '*.css',
            'processors': (
                {'processor': 'gena.processors.SavingProcessor'},
            ),
        },
        ...
    )

    An example of bundling:

    RULES = (
        ...
        {
            'test': '*.css',
            'processors': (
                {
                    'processor': 'gena.processors.FileNameProcessor',
                    'options': {
                        'name': 'bundle.css',
                    },
                },
                {
                    'processor': 'gena.processors.SavingProcessor',
                    'options': {
                        'append': True,
                    },
                },
            ),
        },
        ...
    )
    """

    append = False
    path = ''

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        if not self.path:
            file.path.directory = settings.DST_DIR
        elif callable(self.path):
            file.path.path = self.path(file)
        else:
            file.path.path = self.path.format(file=file)
        file.save(append=self.append)
        return file


class StdoutProcessor(Processor):
    """Write the file contents to `stdout`."""

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        if file.is_text():
            stdout.write(file.contents)
        else:
            stdout.buffer.write(file.contents)
        return file


class TemplateProcessor(TextProcessor):
    """Render templates.

    There are several variables available in templates:
    - the file contents
    - all meta variables of the file
    - all settings variables
    For example, we would like to render our template named article.html:

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {
                    'processor': 'gena.processors.TemplateProcessor',
                    'options': {
                        'template': 'article.html',
                    },
                }
                ...
            ),
        },
        ...
    )

    The default template engine is Jinja2.
    """

    def __init__(self, template: str, engine: Optional[TemplateEngine] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.template = template
        self.engine = engine or JinjaTemplateEngine()

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.contents = self.engine.render(
            self.template,
            {
                'context': context,
                'contents': file.contents,
                **file.meta,
                **settings,
            },
        )

        return file


class TypeProcessor(Processor):
    """Change the file type."""

    type = FileType.TEXT

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.type = self.type
        return file
