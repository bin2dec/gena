from __future__ import annotations

import re

import lxml.html

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from slugify import slugify

from gena.files import FileLike
from gena.settings import settings


__all__ = (
    'BlogAuthor',
    'BlogCategory',
    'BlogPost',
    'BlogTag',
)


@dataclass(unsafe_hash=True)
class BlogAuthor:
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def url(self) -> str:
        return f'/{settings.BLOG_AUTHOR_ARCHIVE_DIR}/{self.slug}/'


@dataclass(unsafe_hash=True)
class BlogCategory:
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def url(self) -> str:
        return f'/{settings.BLOG_CATEGORY_ARCHIVE_DIR}/{self.slug}/'


@dataclass(unsafe_hash=True)
class BlogTag:
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def url(self) -> str:
        return f'/{settings.BLOG_TAG_ARCHIVE_DIR}/{self.slug}/'


@dataclass()
class BlogPost:
    authors: Sequence[BlogAuthor]
    category: BlogCategory
    contents: str
    date: datetime
    slug: str
    tags: Sequence[BlogTag]
    title: str

    @property
    def teaser(self) -> str:
        body = lxml.html.fragment_fromstring(self.contents, 'body')
        body = lxml.html.tostring(body, encoding='unicode')
        teaser = re.split(settings.BLOG_TEASER_REGEXP, body, maxsplit=1)[0]
        teaser = lxml.html.fromstring(teaser)
        teaser = lxml.html.tostring(teaser, encoding='unicode')
        return teaser

    @property
    def url(self) -> str:
        return f'/{settings.BLOG_POSTS_DIR}/{self.slug}/'

    @staticmethod
    def from_file(file: FileLike) -> BlogPost:
        authors = [BlogAuthor(name=author) for author in file.meta.get('authors', ())]
        category = BlogCategory(name=str(file.meta.get('category', '')))
        tags = [BlogTag(name=tag) for tag in file.meta.get('tags', ())]

        post = BlogPost(
            authors=authors,
            category=category,
            contents=file.contents,
            date=file.meta.date[0],
            slug=file.meta.slug[0],
            tags=tags,
            title=file.meta.title[0],
        )

        return post
