"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import logging

from collections import defaultdict
from typing import Optional, Sequence

from gena.context import context
from gena.files import File
from gena.settings import settings
from gena.templating import JinjaTemplateEngine, TemplateEngine


__all__ = (
    'build_author_archive',
    'build_category_archive',
    'build_main_page',
    'build_tag_archive',
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


def build_author_archive(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create an author archive."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the author archive')
        return

    authors = defaultdict(list)
    for post in posts:
        for author in post.authors:
            authors[author].append(post)

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    author_list = File(settings.DST_DIR, settings.BLOG_AUTHORS_DIR, 'index.html')
    author_list.contents = template_engine.render(settings.BLOG_AUTHOR_LIST_TEMPLATE, {'authors': authors, **settings})
    author_list.save()

    for author, posts in authors.items():
        save_posts(posts, directory=f'{settings.DST_DIR}/{settings.BLOG_AUTHORS_DIR}/{author}',
                   template=settings.BLOG_AUTHOR_DETAIL_TEMPLATE, template_engine=template_engine)


def build_category_archive(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a category archive."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the category archive')
        return

    categories = defaultdict(list)
    for post in posts:
        if post.category:
            categories[post.category].append(post)

    category_list = File(settings.DST_DIR, settings.BLOG_CATEGORIES_DIR, 'index.html')
    category_list.contents = template_engine.render(settings.BLOG_CATEGORY_LIST_TEMPLATE,
                                                    {'categories': categories, **settings})
    category_list.save()

    for category, posts in categories.items():
        save_posts(posts, directory=f'{settings.DST_DIR}/{settings.BLOG_CATEGORIES_DIR}/{category}',
                   template=settings.BLOG_CATEGORY_DETAIL_TEMPLATE, template_engine=template_engine)


def build_main_page(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a blog main page."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the main page')
    else:
        save_posts(posts, directory=settings.DST_DIR, template=settings.BLOG_MAIN_PAGE_TEMPLATE,
                   template_engine=template_engine)


def build_tag_archive(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a tag archive."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the tag archive')
        return

    tags = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            tags[tag].append(post)

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    tag_list = File(settings.DST_DIR, settings.BLOG_TAGS_DIR, 'index.html')
    tag_list.contents = template_engine.render(settings.BLOG_TAG_LIST_TEMPLATE, {'tags': tags, **settings})
    tag_list.save()

    for tag, posts in tags.items():
        save_posts(posts, directory=f'{settings.DST_DIR}/{settings.BLOG_TAGS_DIR}/{tag}',
                   template=settings.BLOG_TAG_DETAIL_TEMPLATE, template_engine=template_engine)
