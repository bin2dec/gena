from __future__ import annotations

import jinja2
import subprocess

from abc import ABC, abstractmethod
from collections import defaultdict
from htmlmin import minify as html_minify
from markdown import Markdown
from typing import Callable, Iterable, Optional, Sequence, TypeVar, Union

from gena.context import context
from gena.files import File
from gena.settings import settings


__all__ = (
    'ExternalProcessor',
    'FileMetaProcessor',
    'FileNameProcessor',
    'GroupProcessor',
    'HTMLMinifierProcessor',
    'Jinja2Processor',
    'MarkdownProcessor',
    'SavingProcessor',
    'TemplateProcessor',
)


T = TypeVar('T')
FileCallable = Union[T, Callable[[File], T]]


class Processor(ABC):
    """Abstract base class for all processors."""

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def process(self, file: File) -> File:
        return file


class BinaryProcessor(Processor):
    """Base class for all processors that work with binary files (when file contents are bytes)."""

    def process(self, file: File) -> File:
        if not file.is_binary():
            raise TypeError(f'{self.__class__.__name__} supports binary files only')
        return file


class TextProcessor(Processor):
    """Base class for all processors that work with text files (when file contents are a string)."""

    def process(self, file: File) -> File:
        if not file.is_text():
            raise TypeError(f'{self.__class__.__name__} supports text files only')
        return file


class ExternalProcessor(Processor):
    """Run an external command.

    For example, we would like to compress our JavaScript files that aren't compressed yet:

    PROCESSING_RULES = (
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

    def process(self, file: File) -> File:
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

    PROCESSING_RULES = (
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

    def process(self, file: File) -> File:
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

        return file


class FileNameProcessor(Processor):
    """Change the file name (base name + extension).

    For example, we would like to change extensions of our markdown files (presumably after some markdown processing):

    PROCESSING_RULES = (
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

    def process(self, file: File) -> File:
        if callable(self.name):
            file.path.name = self.name(file)
        else:
            file.path.name = self.name
        return file


class GroupProcessor(Processor):
    """Create groups of files.

    It can be useful in many cases for the final jobs like a job of generation of index file with, for instance, links
    to your articles.
    Let's look at the following rule:

    PROCESSING_RULES = (
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

    According to this rule all our markdown files will be part of the group named `articles` (now globally accessible
    via context.groups['articles']).
    Next, we can use this bunch of the files in some final job to generate an article list.
    Note that it's generally better to place GroupProcessor after SavingProcessor.
    """

    def __init__(self, *, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        if 'groups' not in context:
            context.groups = defaultdict(list)
        self.name = name

    def process(self, file: File) -> File:
        context.groups[self.name].append(file)
        return file


class HTMLMinifierProcessor(TextProcessor):
    """Minify HTML.

    For example, we would like to minify contents of our files that have been processed by MarkdownProcessor:

    PROCESSING_RULES = (
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

    You can also customize the processing by using HTML_MINIFIER_PROCESSOR_OPTIONS in your settings.
    """

    def process(self, file: File) -> File:
        file = super().process(file)
        file.contents = html_minify(file.contents, **settings.HTML_MINIFIER_PROCESSOR_OPTIONS)
        return file


class Jinja2Processor(TextProcessor):
    """Render Jinja2 templates.

    There are several variables available in templates:
    the file contents
    all meta variables of the file
    all settings variables
    For example, we would like to render our template named article.html:

    PROCESSING_RULES = (
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

    def process(self, file: File) -> File:
        file = super().process(file)
        context = {'contents': file.contents, **file.meta, **settings}
        file.contents = self.template.render(context)

        return file


class MarkdownProcessor(TextProcessor):
    """Convert Markdown syntax into HTML.

    For example, we would like to convert all our markdown files:

    PROCESSING_RULES = (
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
    MARKDOWN_PROCESSOR_OPTIONS to your settings file.
    """

    def process(self, file: File) -> File:
        file = super().process(file)
        md = Markdown(**settings.MARKDOWN_PROCESSOR_OPTIONS)
        file.contents = md.convert(file.contents)
        meta = getattr(md, 'Meta', {})
        file.meta.update(meta)
        return file


class SavingProcessor(Processor):
    """Save the file."""

    rename_directory = True

    def process(self, file: File) -> File:
        if self.rename_directory:
            file.path.directory = settings.DST_DIR
        file.save()
        return file


TemplateProcessor = Jinja2Processor  # this is simply an alias for Jinja2Processor
