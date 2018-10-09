"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import logging

from typing import Optional

from gena.context import context
from gena.files import File
from gena.settings import settings
from gena.templating import JinjaTemplateEngine, TemplateEngine


__all__ = (
    'build_main_page',
)


logger = logging.getLogger(__name__)


def build_main_page(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a blog main page."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the main page')
        return

    # Split blog posts up into groups depending on BLOG_POSTS_PER_PAGE
    if settings.BLOG_POSTS_PER_PAGE:
        groups = [posts[i:i+settings.BLOG_POSTS_PER_PAGE] for i in range(0, len(posts), settings.BLOG_POSTS_PER_PAGE)]
    else:  # BLOG_POSTS_PER_PAGE = 0
        groups = [posts]

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    groups_num = len(groups)

    # Create a page for each blog post group (index.html...indexN.html)
    for i, group in enumerate(groups, start=1):
        template_context = {'posts': group}

        if i == 1:  # the first page
            template_context['previous_page'] = None
            file = File(settings.DST_DIR, 'index.html')
        else:
            template_context['previous_page'] = 'index.html' if i == 2 else f'index{i-1}.html'
            file = File(settings.DST_DIR, f'index{i}.html')

        if i == groups_num:  # the last page
            template_context['next_page'] = None
        else:
            template_context['next_page'] = f'index{i+1}.html'

        file.contents = template_engine.render(settings.BLOG_MAIN_PAGE_TEMPLATE, template_context)
        file.save()
