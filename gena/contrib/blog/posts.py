from __future__ import annotations

import re

import lxml.html

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence

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

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def url(self):
        return f'/{settings.BLOG_AUTHORS_DIR}/{self.slug}/'


@dataclass(unsafe_hash=True)
class BlogCategory:
    name: str

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def url(self):
        return f'/{settings.BLOG_CATEGORIES_DIR}/{self.slug}/'


@dataclass(unsafe_hash=True)
class BlogTag:
    name: str

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def url(self):
        return f'/{settings.BLOG_TAGS_DIR}/{self.slug}/'


@dataclass()
class BlogPost:
    authors: Sequence[BlogAuthor]
    category: BlogCategory
    date: datetime
    slug: str
    tags: Sequence[BlogTag]
    teaser: str
    title: str
    contents: Optional[str] = None

    @property
    def url(self):
        return f'/{settings.BLOG_POSTS_DIR}/{self.slug}/'

    @staticmethod
    def from_file(file: FileLike, store_contents: bool = False) -> BlogPost:
        # authors
        authors = [BlogAuthor(name=author) for author in file.meta.get('authors', ())]

        # category
        category = BlogCategory(name=str(file.meta.get('category', '')))

        # tags
        tags = [BlogTag(name=tag) for tag in file.meta.get('tags', ())]

        # teaser
        body = lxml.html.fragment_fromstring(file.contents, 'body')
        body = lxml.html.tostring(body, encoding='unicode')
        teaser = re.split(settings.BLOG_TEASER_REGEXP, body, maxsplit=1)[0]
        teaser = lxml.html.fromstring(teaser)
        teaser = lxml.html.tostring(teaser, encoding='unicode')

        post = BlogPost(
            authors=authors,
            category=category,
            date=file.meta.date[0],
            slug=file.meta.slug[0],
            tags=tags,
            teaser=teaser,
            title=file.meta.title[0],
        )

        if store_contents:
            post.contents = file.contents

        return post
