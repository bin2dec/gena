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
    def __init__(self, loc: str, lastmod: Optional[datetime] = None):
        self.loc = loc
        self.lastmod = datetime.now() if lastmod is None else lastmod

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
