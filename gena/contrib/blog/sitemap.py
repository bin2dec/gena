from __future__ import annotations

from dataclasses import dataclass


__all__ = (
    'SitemapEntry',
)


@dataclass()
class SitemapEntry:
    loc: str
