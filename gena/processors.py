from __future__ import annotations

import logging
import subprocess

from abc import ABC, abstractmethod
from collections import defaultdict
from sys import stdout
from typing import Callable, Iterable, Optional, Sequence, TypeVar, Union

import jinja2

from htmlmin import minify as html_minify
from markdown import Markdown

from gena.context import context
from gena.files import FileLike, FileType
from gena.settings import settings
from gena.utils import map_as_kwargs


__all__ = (
    'BinaryProcessor',
    'BundleProcessor',
    'ExternalProcessor',
    'FileMetaProcessor',
    'FileNameProcessor',
    'GroupProcessor',
    'HTMLMinifierProcessor',
    'Jinja2Processor',
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
            logger.debug('%s(%s) is processing %r', self.__class__.__name__, map_as_kwargs(self.__dict__), file)
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
        <style>{{ context.bundles.css }}</style>
        ...
    </head>
    ...

    Notice that all bundled files must be the same type (binary or text).
    """

    section = 'bundles'

    def __init__(self, *, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.section not in context:
            context[self.section] = {}
        self.name = name

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        try:
            context[self.section][self.name] += file.contents
        except KeyError:
            context[self.section][self.name] = file.contents
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
                        'name': lambda file: f'{file.path.basename}.min.js',
                    },
                },
                ...
            ),
        },
        ...
    )

    Here we used third-party minifier called UglifyJS (http://lisperator.net/uglifyjs/) to compress these files.
    """

    def __init__(self, *, command: Sequence[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self.command = command

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        output = subprocess.run(self.command,
                                input=file.contents,
                                shell=False,
                                stdout=subprocess.PIPE,
                                text=file.is_text() or None,
                                **settings.EXTERNAL_PROCESSOR)
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
                        'name': lambda file: f'{file.basename}.html',
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
            file.path.name = self.name
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
    via context.groups['articles'] if `section` is 'groups').
    Next, we can use this bunch of the files in some final job to generate an article list.
    Note that it's generally better to place GroupProcessor after SavingProcessor.
    """

    section = 'groups'

    def __init__(self, *, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.section not in context:
            context.groups = defaultdict(list)
        self.name = name

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        context[self.section][self.name].append(file)
        return file


class HTMLMinifierProcessor(TextProcessor):
    """Minify HTML.

    For example, we would like to minify the contents of our files that have been processed by MarkdownProcessor:

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {'processor': 'gena.processors.MarkdownProcessor'},      # we do markdown processing first
                ...
                {'processor': 'gena.processors.HTMLMinifierProcessor'},  # then we run our minifier
                ...
            ),
        },
        ...
    )

    You can also customize the processing by using HTML_MINIFIER_OPTIONS in your settings.
    """

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.contents = html_minify(file.contents, **settings.HTML_MINIFIER_OPTIONS)
        return file


class Jinja2Processor(TextProcessor):
    """Render Jinja2 templates.

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

    The processor uses settings.TEMPLATE_DIRS to find templates. TEMPLATE_DIRS can be a string or a list of strings
    if multiple locations are wanted.
    """

    def __init__(self, template: str, **kwargs) -> None:
        super().__init__(**kwargs)

        loader = jinja2.FileSystemLoader(searchpath=settings.TEMPLATE_DIRS)
        environment = jinja2.Environment(loader=loader, **settings.JINJA2_OPTIONS)
        self.template = environment.get_template(template)

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        variables = {'context': context, 'contents': file.contents, **file.meta, **settings}
        file.contents = self.template.render(variables)

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
    directory = None

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        if self.directory is None:
            file.path.directory = settings.DST_DIR
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


class TypeProcessor(Processor):
    """Change the file type."""

    type = FileType.TEXT

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.type = self.type
        return file


TemplateProcessor = Jinja2Processor  # this is simply an alias for Jinja2Processor
