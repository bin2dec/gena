"""Markdown extensions."""

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from gena.settings import settings


__all__ = (
    'SettingsExtension',
)


class SettingsPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        pattern = kwargs.pop('pattern', r'({{\s*([A-Z0-9_]+)\s*}})')
        self.pattern = re.compile(pattern)
        self.default = kwargs.pop('default', '')
        super().__init__(*args, **kwargs)

    def _replace(self, match):
        return settings.get(match.group(2), self.default)

    def run(self, lines):
        new_lines = []
        for line in lines:
            new_lines.append(self.pattern.sub(self._replace, line))
        return new_lines


class SettingsExtension(Extension):
    """Replace all {{ SETTING }} with an appropriate setting."""

    def extendMarkdown(self, md):
        md.preprocessors.register(SettingsPreprocessor(md), 'gena_settings', 10)
