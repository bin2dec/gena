"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import logging

from collections import defaultdict
from typing import Mapping, Optional, Sequence

from lxml import etree

from gena.context import context
from gena.exceptions import JobError
from gena.files import File, FileType
from gena.settings import settings
from gena.templating import JinjaTemplateEngine, TemplateEngine
from gena.utils import UserDict


__all__ = (
    'build_archive',
    'build_authors',
    'build_categories',
    'build_main_page',
    'build_sitemap',
    'build_tags',
)


logger = logging.getLogger(__name__)


def save_posts(posts: Sequence, *, directory: str, template: str, template_engine: Optional[TemplateEngine] = None,
               extra_context: Optional[Mapping] = None):
    """Save a blog post list."""

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    if extra_context is None:
        extra_context = {}

    # Sort posts by creation date
    posts = sorted(posts, key=lambda post: post.date, reverse=True)

    # Split blog posts up into groups depending on BLOG_POSTS_PER_PAGE
    if settings.BLOG_POSTS_PER_PAGE:
        groups = [posts[i:i+settings.BLOG_POSTS_PER_PAGE] for i in range(0, len(posts), settings.BLOG_POSTS_PER_PAGE)]
    else:  # BLOG_POSTS_PER_PAGE = 0
        groups = [posts]

    groups_num = len(groups)

    # Create a page for each blog post group (index.html...indexN.html).
    # Save this page into a given directory
    for i, group in enumerate(groups, start=1):
        template_context = {'posts': group, **extra_context, **settings}

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


def build_archive(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a post archive."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the post archive')
        return

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    years = UserDict()
    for post in posts:
        year, month = post.date.timetuple()[:2]

        try:
            years[year]['posts'].append(post)
        except KeyError:
            years[year] = UserDict(
                months=UserDict(),
                posts=[post],
                url=f'/{settings.BLOG_ARCHIVE_DIR}/{year}/',
            )

        months = years[year]['months']

        try:
            months[month]['posts'].append(post)
        except KeyError:
            months[month] = UserDict(
                posts=[post],
                url=f'/{settings.BLOG_ARCHIVE_DIR}/{year}/{month}/',
            )

    archive = File(settings.DST_DIR, settings.BLOG_ARCHIVE_DIR, 'index.html')
    archive.contents = template_engine.render(settings.BLOG_ARCHIVE_TEMPLATE, {'years': years, **settings})
    archive.save()

    for year, y_data in years.items():
        save_posts(y_data['posts'], directory=f'{settings.DST_DIR}/{settings.BLOG_ARCHIVE_DIR}/{year}',
                   template=settings.BLOG_YEAR_DETAIL_TEMPLATE, template_engine=template_engine,
                   extra_context={'year': year})

        for month, m_data in y_data['months'].items():
            save_posts(m_data['posts'], directory=f'{settings.DST_DIR}/{settings.BLOG_ARCHIVE_DIR}/{year}/{month}',
                       template=settings.BLOG_MONTH_DETAIL_TEMPLATE, template_engine=template_engine,
                       extra_context={'year': year, 'month': month})


def build_authors(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create author pages."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the author pages')
        return

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    authors = defaultdict(list)
    for post in posts:
        for author in post.authors:
            authors[author].append(post)

    author_list = File(settings.DST_DIR, settings.BLOG_AUTHORS_DIR, 'index.html')
    author_list.contents = template_engine.render(settings.BLOG_AUTHOR_LIST_TEMPLATE, {'authors': authors, **settings})
    author_list.save()

    for author, posts in authors.items():
        save_posts(posts, directory=f'{settings.DST_DIR}/{settings.BLOG_AUTHORS_DIR}/{author.slug}',
                   template=settings.BLOG_AUTHOR_DETAIL_TEMPLATE, template_engine=template_engine)


def build_categories(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create category pages."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the category pages')
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
        save_posts(posts, directory=f'{settings.DST_DIR}/{settings.BLOG_CATEGORIES_DIR}/{category.slug}',
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


def build_sitemap() -> None:
    """Create sitemap.xml."""

    if not settings.BLOG_SITEMAP:
        return

    try:
        entries = context[settings.BLOG_CONTEXT_SITEMAP]
    except KeyError:
        raise JobError('No sitemap entries are found to build "sitemap.xml"', build_sitemap)

    urlset = etree.Element('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    for entry in entries:
        url = etree.SubElement(urlset, 'url')
        loc = etree.SubElement(url, 'loc')
        loc.text = entry.loc

    sitemap = File(settings.DST_DIR, 'sitemap.xml', type=FileType.BINARY)
    sitemap.contents = etree.tostring(urlset, encoding='utf-8', xml_declaration=True)
    sitemap.save()


def build_tags(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create tag pages."""

    try:
        posts = context.blog_posts
    except AttributeError:
        logger.warning('no blog posts are found to build the tag pages')
        return

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    tags = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            tags[tag].append(post)

    tag_list = File(settings.DST_DIR, settings.BLOG_TAGS_DIR, 'index.html')
    tag_list.contents = template_engine.render(settings.BLOG_TAG_LIST_TEMPLATE, {'tags': tags, **settings})
    tag_list.save()

    for tag, posts in tags.items():
        save_posts(posts, directory=f'{settings.DST_DIR}/{settings.BLOG_TAGS_DIR}/{tag.slug}',
                   template=settings.BLOG_TAG_DETAIL_TEMPLATE, template_engine=template_engine)
