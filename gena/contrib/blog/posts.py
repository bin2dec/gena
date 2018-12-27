from __future__ import annotations

import re

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Sequence

import lxml.html

from slugify import slugify

from gena.files import FileLike
from gena.settings import settings


__all__ = (
    'BlogPost',
    'BlogPostAuthor',
    'BlogPostCategory',
    'BlogPostStatus',
    'BlogPostTag',
)


class BlogPostStatus(Enum):
    DRAFT = 'draft'
    PRIVATE = 'private'
    PUBLIC = 'public'


@dataclass(unsafe_hash=True)
class BlogPostAuthor:
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def url(self) -> str:
        return f'{settings.BLOG_AUTHORS_URL}/{self.slug}/'


@dataclass(unsafe_hash=True)
class BlogPostCategory:
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def url(self) -> str:
        return f'{settings.BLOG_CATEGORIES_URL}/{self.slug}/'


@dataclass(unsafe_hash=True)
class BlogPostTag:
    name: str

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def url(self) -> str:
        return f'{settings.BLOG_TAGS_URL}/{self.slug}/'


@dataclass()
class BlogPost:
    authors: Sequence[BlogPostAuthor]
    category: BlogPostCategory
    contents: str
    date: datetime
    modified: datetime
    slug: str
    status: BlogPostStatus
    tags: Sequence[BlogPostTag]
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
        return f'{settings.BLOG_POSTS_URL}/{self.slug}/'

    @staticmethod
    def from_file(file: FileLike) -> BlogPost:
        authors = [BlogPostAuthor(name=author) for author in file.meta.get('authors', ())]
        category = BlogPostCategory(name=str(file.meta.get('category', '')))
        if 'status' in file.meta:
            status = BlogPostStatus(file.meta.status[0].lower())
        else:
            status = BlogPostStatus.PUBLIC
        tags = [BlogPostTag(name=tag) for tag in file.meta.get('tags', ())]

        post = BlogPost(
            authors=authors,
            category=category,
            contents=file.contents,
            date=file.meta.date[0],
            modified=file.meta.modified[0],
            slug=file.meta.slug[0],
            status=status,
            tags=tags,
            title=file.meta.title[0],
        )

        return post
