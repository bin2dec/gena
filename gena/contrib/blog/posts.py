from __future__ import annotations

import re

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Sequence

import lxml.html

from slugify import slugify

from gena.files import FileLike
from gena.settings import settings


__all__ = (
    'BlogPost',
    'BlogPostAuthor',
    'BlogPostCategory',
    'BlogPostTag',
)


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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BlogPostTag):
            return self.name == other.name
        return False

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, BlogPostTag):
            return self.name > other.name
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, BlogPostTag):
            return self.name < other.name
        return False

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
    description: str
    draft: bool
    modified: datetime
    slug: str
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
        draft = str(file.meta.get('status', '')).lower() == 'draft'
        tags = [BlogPostTag(name=tag) for tag in file.meta.get('tags', ())]
        tags.sort()

        post = BlogPost(
            authors=authors,
            category=category,
            contents=file.contents,
            date=file.meta.date[0],
            description=str(file.meta.get('description', '')),
            draft=draft,
            modified=file.meta.modified[0],
            slug=file.meta.slug[0],
            tags=tags,
            title=file.meta.title[0],
        )

        return post
