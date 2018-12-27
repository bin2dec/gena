from __future__ import annotations

import urllib.parse

from datetime import datetime
from typing import Optional
from xml.sax import saxutils

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


class SitemapEntry:
    def __init__(self, loc: str, lastmod: Optional[datetime] = None, changefreq: Optional[str] = None,
                 priority: Optional[float] = None, **kwargs):

        self.loc = loc
        self.lastmod = lastmod or datetime.now()
        self.changefreq = changefreq or settings.BLOG_SITEMAP_DEFAULT_CHANGEFREQ
        self.priority = priority or settings.BLOG_SITEMAP_DEFAULT_PRIORITY

    @property
    def loc(self) -> str:
        return self._loc

    @loc.setter
    def loc(self, value: str) -> None:
        url = urllib.parse.urlsplit(value)
        path = urllib.parse.quote(url.path, safe='/&\'"><=')
        path = saxutils.escape(path, {'\'': '&apos;', '"': '&quot;'})
        new_url = urllib.parse.urlunsplit((url.scheme, url.netloc, path, url.query, url.fragment))

        if len(new_url) > settings.BLOG_SITEMAP_LOC_SIZE:
            raise ValueError(f'a sitemap URL must be less than {settings.BLOG_SITEMAP_LOC_SIZE} characters')

        self._loc = new_url

    @property
    def changefreq(self) -> str:
        return self._changefreq

    @changefreq.setter
    def changefreq(self, value: str) -> None:
        if value in settings.BLOG_SITEMAP_CHANGEFREQ_LIST:
            self._changefreq = value
        else:
            raise ValueError(f'"{value}" is an invalid value for sitemap changefreq')

    @property
    def priority(self) -> float:
        return self._priority

    @priority.setter
    def priority(self, value: float) -> None:
        if settings.BLOG_SITEMAP_PRIORITY_RANGE[0] <= value <= settings.BLOG_SITEMAP_PRIORITY_RANGE[1]:
            self._priority = value
        else:
            raise ValueError(f'a sitemap priority must be within a range '
                             f'from {settings.BLOG_SITEMAP_PRIORITY_RANGE[0]} '
                             f'to {settings.BLOG_SITEMAP_PRIORITY_RANGE[1]}')
