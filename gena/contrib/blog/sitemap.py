from __future__ import annotations

from dataclasses import dataclass

from gena.context import context
from gena.settings import settings


__all__ = (
    'add_sitemap_entry_to_context',
    'SitemapEntry',
)


def add_sitemap_entry_to_context(loc: str, **kwargs) -> None:
    if settings.BLOG_SITEMAP:
        sitemap_entry = SitemapEntry(loc, **kwargs)
        context.add_to_list(settings.BLOG_CONTEXT_SITEMAP, sitemap_entry)


@dataclass()
class SitemapEntry:
    loc: str
