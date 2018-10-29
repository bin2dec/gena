"""Blog extension processors."""

from __future__ import annotations

import re

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import lxml.html

from gena.context import context
from gena.files import FileLike
from gena.processors import TextProcessor
from gena.settings import settings


__all__ = (
    'BlogPostProcessor',
)


@dataclass()
class BlogAuthor:
    name: str


@dataclass()
class BlogPost:
    authors: list
    date: datetime
    slug: str
    teaser: str
    title: str
    contents: Optional[str] = None

    @property
    def url(self):
        return f'/{settings.BLOG_POSTS_DIR}/{self.slug}/'


class BlogPostProcessor(TextProcessor):
    contents = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._posts = context.add_item(settings.BLOG_CONTEXT_POSTS, [])
        self._teaser_regexp = re.compile(settings.BLOG_TEASER_REGEXP)

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)

        # authors
        authors = [BlogAuthor(name=author) for author in file.meta.author]

        # teaser
        body = lxml.html.fragment_fromstring(file.contents, 'body')
        body = lxml.html.tostring(body, encoding='unicode')
        teaser = self._teaser_regexp.split(body, maxsplit=1)[0]
        teaser = lxml.html.fromstring(teaser)
        teaser = lxml.html.tostring(teaser, encoding='unicode')

        post = BlogPost(
            authors=authors,
            date=file.meta.date[0],
            slug=file.meta.slug[0],
            teaser=teaser,
            title=file.meta.title[0],
        )

        if self.contents:
            post.contents = file.contents

        self._posts.append(post)

        return file
