"""Blog extension processors."""

from __future__ import annotations

from typing import Optional

from gena.context import context
from gena.contrib.blog.posts import BlogPost, BlogStatus
from gena.contrib.blog.sitemap import SitemapEntry
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

        if post.status == BlogStatus.DRAFT:
            raise StopProcessing(f'The blog post "{post.title}" is a draft', processor=self, file=file)
        elif post.status == BlogStatus.PUBLIC:
            context.add_to_list(settings.BLOG_CONTEXT_POSTS, post)
            if settings.BLOG_SITEMAP:
                sitemap_entry = SitemapEntry(loc=post.url)
                context.add_to_list(settings.BLOG_CONTEXT_SITEMAP, sitemap_entry)

        file.contents = self.template_engine.render(settings.BLOG_POST_TEMPLATE, {'post': post, **settings})

        return file


class SitemapProcessor(Processor):
    def __init__(self, loc: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.loc = loc

    def process(self, file: FileLike) -> FileLike:
        file = super().process(file)

        if settings.BLOG_SITEMAP:
            sitemap_entry = SitemapEntry(loc=self.loc.format(file=file))
            context.add_to_list(settings.BLOG_CONTEXT_SITEMAP, sitemap_entry)

        return file
