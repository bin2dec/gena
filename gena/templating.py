"""GenA template engines."""

from __future__ import annotations

import os

from abc import ABC, abstractmethod
from typing import Dict, Optional

import jinja2

from gena.settings import settings


__all__ = (
    'JinjaTemplateEngine',
    'TemplateEngine',
)


class TemplateEngine(ABC):
    """Abstract base class for all template engines."""

    @abstractmethod
    def render(self, template: str, context: Dict) -> str:
        """Render templates."""
        pass


class JinjaTemplateEngine(TemplateEngine):
    """Jinja2 template engine."""

    def __init__(self) -> None:
        jinja_loader = jinja2.FileSystemLoader(settings.TEMPLATE_DIRS)
        if settings.CACHE_DIR:
            cache_dir = os.path.join(settings.CACHE_DIR, 'jinja')
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            jinja_cache: Optional[jinja2.BytecodeCache] = jinja2.FileSystemBytecodeCache(cache_dir, '%s.cache')
        else:
            jinja_cache = None

        self._jinja_environment = jinja2.Environment(loader=jinja_loader, bytecode_cache=jinja_cache,
                                                     **settings.JINJA_OPTIONS)

    def render(self, template: str, context: Optional[Dict] = None) -> str:
        jinja_template = self._jinja_environment.get_template(template)
        if context:
            return jinja_template.render(context)
        return jinja_template.render()
