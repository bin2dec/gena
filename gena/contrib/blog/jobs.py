"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import logging

from typing import Optional, Sequence

from gena.context import context
from gena.files import File
from gena.settings import settings
from gena.templating import JinjaTemplateEngine, TemplateEngine


__all__ = (
    'build_main_page',
)


logger = logging.getLogger(__name__)


def save_posts(posts: Sequence, *, directory: str, template: str, template_engine: Optional[TemplateEngine] = None):
    """Save a blog post list."""

    # Split blog posts up into groups depending on BLOG_POSTS_PER_PAGE
    if settings.BLOG_POSTS_PER_PAGE:
        groups = [posts[i:i+settings.BLOG_POSTS_PER_PAGE] for i in range(0, len(posts), settings.BLOG_POSTS_PER_PAGE)]
    else:  # BLOG_POSTS_PER_PAGE = 0
        groups = [posts]

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    groups_num = len(groups)

    # Create a page for each blog post group (index.html...indexN.html).
    # Save this page into a given directory
    for i, group in enumerate(groups, start=1):
        template_context = {'posts': group, **settings}

        if i == 1:  # the first page
            template_context['previous_page'] = None
            file = File(directory, 'index.html')
        else:
            template_context['previous_page'] = 'index.html' if i == 2 else f'index{i-1}.html'
            file = File(directory, f'index{i}.html')

        if i == groups_num:  # the last page
            template_context['next_page'] = None
        else:
            template_context['next_page'] = f'index{i+1}.html'

        file.contents = template_engine.render(template, template_context)
        file.save()


def build_main_page(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a blog main page."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the main page')
    else:
        save_posts(posts, directory=settings.DST_DIR, template=settings.BLOG_MAIN_PAGE_TEMPLATE,
                   template_engine=template_engine)
