"""Blog extension processors."""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Optional

import lxml.html

from gena.context import context
from gena.files import FileLike, FileMetaValue
from gena.processors import TextProcessor
from gena.settings import settings


__all__ = (
    'BlogPostProcessor',
)


@dataclass()
class Post:
    author: FileMetaValue
    date: FileMetaValue
    teaser: str
    title: FileMetaValue
    url: str
    contents: Optional[str] = None


class BlogPostProcessor(TextProcessor):
    contents = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._posts = context.add_item(settings.BLOG_CONTEXT_POSTS, [])
        self._teaser_regexp = re.compile(settings.BLOG_TEASER_REGEXP)

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)

        body = lxml.html.fragment_fromstring(file.contents, 'body')
        body = lxml.html.tostring(body, encoding='unicode')
        teaser = self._teaser_regexp.split(body, maxsplit=1)[0]
        teaser = lxml.html.fromstring(teaser)
        teaser = lxml.html.tostring(teaser, encoding='unicode')

        post = Post(
            author=file.meta.author,
            date=file.meta.date,
            teaser=teaser,
            title=file.meta.title,
            url=f'{settings.BLOG_POSTS_DIR}/{file.meta.slug}/',
        )

        if self.contents:
            post.contents = file.contents

        self._posts.append(post)

        return file
