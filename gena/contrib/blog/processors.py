"""Blog extension processors."""

from __future__ import annotations

from typing import Optional

from gena.context import context
from gena.contrib.blog.posts import BlogPost, BlogPostStatus
from gena.contrib.blog.sitemap import add_sitemap_entry_to_context
from gena.exceptions import StopProcessing
from gena.files import FileLike
from gena.processors import Processor, TextProcessor
from gena.settings import settings
from gena.templating import JinjaTemplateEngine, TemplateEngine


__all__ = (
    'BlogPostProcessor',
    'SitemapProcessor',
)


class BlogPostProcessor(TextProcessor):
    def __init__(self, template_engine: Optional[TemplateEngine] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.template_engine = template_engine or JinjaTemplateEngine()

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)

        post = BlogPost.from_file(file)

        if post.status == BlogPostStatus.DRAFT:
            raise StopProcessing(f'The blog post "{post.title}" is a draft', processor=self, file=file)
        elif post.status == BlogPostStatus.PUBLIC:
            context.add_to_list(settings.BLOG_CONTEXT_POSTS, post)
            add_sitemap_entry_to_context(post.url)

        file.contents = self.template_engine.render(settings.BLOG_POST_TEMPLATE, {'post': post, **settings})

        return file


class SitemapProcessor(Processor):
    def __init__(self, loc: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.loc = loc

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)
        add_sitemap_entry_to_context(self.loc.format(file=file))
        return file
