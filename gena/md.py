"""Markdown extensions."""

import re

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from slugify import slugify

from gena.settings import settings


__all__ = (
    'SettingsExtension',
    'SlugsExtension',
)


class SettingsInlineProcessor(InlineProcessor):
    """The processor for SettingsExtension."""

    def handleMatch(self, m, data):
        return settings.get(m.group(2), ''), m.start(0), m.end(0)


class SettingsExtension(Extension):
    """Replace all ::KEY:: with appropriate values from the settings dictionary."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(SettingsInlineProcessor(r'(::\s*([A-Z0-9_]+?)\s*::)'), 'gena_settings', 200)


class SlugsPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        pattern = kwargs.pop('pattern', r'(<!\s*(.+?)\s*!>)')
        self.pattern = re.compile(pattern)
        self.default = kwargs.pop('default', '')
        super().__init__(*args, **kwargs)

    def _replace(self, match):
        return slugify(match.group(2))

    def run(self, lines):
        new_lines = []
        for line in lines:
            new_lines.append(self.pattern.sub(self._replace, line))
        return new_lines


class SlugsExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(SlugsPreprocessor(md), 'gena_slugs', 10)
