"""Blog extension processors."""

from __future__ import annotations

from gena.context import context
from gena.contrib.blog.posts import BlogPost
from gena.files import FileLike
from gena.processors import TextProcessor
from gena.settings import settings


__all__ = (
    'BlogPostProcessor',
)


class BlogPostProcessor(TextProcessor):
    contents = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._posts = context.add_item(settings.BLOG_CONTEXT_POSTS, [])

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)

        post = BlogPost.from_file(file, self.contents)
        self._posts.append(post)

        return file
