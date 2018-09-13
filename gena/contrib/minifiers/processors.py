"""Minifier processors."""

from __future__ import annotations

from htmlmin import minify as html_minify

from gena.files import FileLike
from gena.processors import TextProcessor

from gena.contrib.minifiers.settings import HTML_MINIFIER_OPTIONS


__all__ = (
    'HTMLMinifierProcessor',
)


class HTMLMinifierProcessor(TextProcessor):
    """Minify HTML.

    For example, we would like to minify the contents of our files that have been processed by MarkdownProcessor:

    RULES = (
        ...
        {
            'test': '*.md',
            'processors': (
                ...
                {'processor': 'gena.processors.MarkdownProcessor'},             # we do markdown processing first
                ...
                {'processor': 'gena.contrib.minifiers.HTMLMinifierProcessor'},  # then we run our minifier
                ...
            ),
        },
        ...
    )

    You can also customize the processing by using HTML_MINIFIER_OPTIONS in your settings.
    """

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        file.contents = html_minify(file.contents, **HTML_MINIFIER_OPTIONS)
        return file
