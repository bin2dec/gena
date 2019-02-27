"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import gzip
import logging

from collections import defaultdict
from typing import Mapping, Optional, Sequence

from lxml import etree

from gena.context import context
from gena.contrib.blog.sitemap import add_sitemap_entry_to_context, SitemapEntry
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
        template_context = {'context': context, 'posts': group, **extra_context, **settings}

        if i == 1:  # the first page
            template_context['next_page'] = None
            file = File(directory, settings.BLOG_INDEX_FILE)
        else:
            template_context['next_page'] = settings.BLOG_INDEX_FILE if i == 2 \
                else settings.BLOG_N_INDEX_FILE.format(i-1)
            file = File(directory, settings.BLOG_N_INDEX_FILE.format(i))

        if i == groups_num:  # the last page
            template_context['previous_page'] = None
        else:
            template_context['previous_page'] = settings.BLOG_N_INDEX_FILE.format(i+1)

        file.contents = template_engine.render(template, template_context)
        file.save()


def build_archive(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a post archive."""

    try:
        posts = context[settings.BLOG_CONTEXT_POSTS]
    except KeyError:
        raise JobError('No blog posts are found to build the post archive')

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
                url=f'{settings.BLOG_ARCHIVE_URL}/{year}/',
            )

        months = years[year]['months']

        try:
            months[month]['posts'].append(post)
        except KeyError:
            months[month] = UserDict(
                posts=[post],
                url=f'{settings.BLOG_ARCHIVE_URL}/{year}/{month}/',
            )

    archive = File(settings.BLOG_ARCHIVE_DIR, settings.BLOG_INDEX_FILE)
    archive.contents = template_engine.render(
        settings.BLOG_ARCHIVE_TEMPLATE,
        {
            'context': context,
            'years': years,
            **settings,
        }
    )
    archive.save()

    add_sitemap_entry_to_context(f'{settings.BLOG_ARCHIVE_URL}/')

    for year, y_data in years.items():
        save_posts(y_data['posts'], directory=f'{settings.BLOG_ARCHIVE_DIR}/{year}',
                   template=settings.BLOG_YEAR_DETAIL_TEMPLATE, template_engine=template_engine,
                   extra_context={'year': year})
        add_sitemap_entry_to_context(y_data['url'])

        for month, m_data in y_data['months'].items():
            save_posts(m_data['posts'], directory=f'{settings.BLOG_ARCHIVE_DIR}/{year}/{month}',
                       template=settings.BLOG_MONTH_DETAIL_TEMPLATE, template_engine=template_engine,
                       extra_context={'year': year, 'month': month})
            add_sitemap_entry_to_context(m_data['url'])


def build_authors(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create author pages."""

    try:
        posts = context[settings.BLOG_CONTEXT_POSTS]
    except KeyError:
        raise JobError('No blog posts are found to build the author pages')

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    authors = defaultdict(list)
    for post in posts:
        for author in post.authors:
            authors[author].append(post)

    author_list = File(settings.BLOG_AUTHORS_DIR, settings.BLOG_INDEX_FILE)
    author_list.contents = template_engine.render(
        settings.BLOG_AUTHOR_LIST_TEMPLATE,
        {
            'context': context,
            'authors': authors,
            **settings,
        }
    )
    author_list.save()

    add_sitemap_entry_to_context(f'{settings.BLOG_AUTHORS_URL}/')

    for author, posts in authors.items():
        save_posts(posts, directory=f'{settings.BLOG_AUTHORS_DIR}/{author.slug}',
                   template=settings.BLOG_AUTHOR_DETAIL_TEMPLATE, template_engine=template_engine)
        add_sitemap_entry_to_context(f'{settings.BLOG_AUTHORS_URL}/{author.slug}/')


def build_categories(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create category pages."""

    try:
        posts = context[settings.BLOG_CONTEXT_POSTS]
    except KeyError:
        raise JobError('No blog posts are found to build the category pages')

    categories = defaultdict(list)
    for post in posts:
        if post.category:
            categories[post.category].append(post)

    category_list = File(settings.BLOG_CATEGORIES_DIR, settings.BLOG_INDEX_FILE)
    category_list.contents = template_engine.render(
        settings.BLOG_CATEGORY_LIST_TEMPLATE,
        {
            'categories': categories,
            'context': context,
            **settings,
        }
    )
    category_list.save()

    add_sitemap_entry_to_context(f'{settings.BLOG_CATEGORIES_URL}/')

    for category, posts in categories.items():
        save_posts(posts, directory=f'{settings.BLOG_CATEGORIES_DIR}/{category.slug}',
                   template=settings.BLOG_CATEGORY_DETAIL_TEMPLATE, template_engine=template_engine)
        add_sitemap_entry_to_context(f'{settings.BLOG_CATEGORIES_URL}/{category.slug}/')


def build_main_page(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create a blog main page."""

    try:
        posts = context[settings.BLOG_CONTEXT_POSTS]
    except KeyError:
        raise JobError('No blog posts are found to build the main page')
    else:
        save_posts(posts, directory=settings.DST_DIR, template=settings.BLOG_MAIN_PAGE_TEMPLATE,
                   template_engine=template_engine)
        add_sitemap_entry_to_context(f'{settings.BLOG_URL}/')


def build_sitemap() -> None:
    """Create sitemap.xml."""

    if not settings.BLOG_SITEMAP:
        return

    try:
        entries = context[settings.BLOG_CONTEXT_SITEMAP]
    except KeyError:
        raise JobError('No sitemap entries are found to build "sitemap.xml"', build_sitemap)

    if settings.BLOG_SITEMAP_SIZE and len(entries) > settings.BLOG_SITEMAP_SIZE:
        groups = [entries[i:i+settings.BLOG_SITEMAP_SIZE] for i in range(0, len(entries), settings.BLOG_SITEMAP_SIZE)]
        filename = settings.BLOG_N_SITEMAP_FILENAME

        # Build a sitemap index
        sitemapindex = etree.Element('sitemapindex', {'xmlns': settings.BLOG_SITEMAP_SCHEMA})

        for i in range(1, len(groups) + 1):
            entry = SitemapEntry(f'{settings.BLOG_URL}/{settings.BLOG_N_SITEMAP_FILENAME.format(i)}')

            sitemap = etree.SubElement(sitemapindex, 'sitemap')
            loc = etree.SubElement(sitemap, 'loc')
            loc.text = entry.loc
            lastmod = etree.SubElement(sitemap, 'lastmod')
            lastmod.text = entry.lastmod.isoformat()

        sitemap_file = File(f'{settings.BLOG_SITEMAP_FILENAME}', type=FileType.BINARY)
        sitemap_file.contents = etree.tostring(sitemapindex, encoding='utf-8', xml_declaration=True)
        if len(sitemap_file.contents) > settings.BLOG_SITEMAP_FILE_SIZE:
            raise JobError(f'The sitemap file is too big (> {settings.BLOG_SITEMAP_FILE_SIZE} bytes)')
        if settings.BLOG_SITEMAP_GZIP:
            sitemap_file.contents = gzip.compress(sitemap_file.contents, compresslevel=settings.GZIP_COMPRESS_LEVEL)
        sitemap_file.save()
    else:
        groups = [entries]
        filename = settings.BLOG_SITEMAP_FILENAME

    # Build a sitemap or multiple sitemaps
    for i, group in enumerate(groups, start=1):
        urlset = etree.Element('urlset', {'xmlns': settings.BLOG_SITEMAP_SCHEMA})

        for entry in group:  # an each group contains BLOG_SITEMAP_SIZE-entries
            url = etree.SubElement(urlset, 'url')

            loc = etree.SubElement(url, 'loc')
            loc.text = entry.loc

            lastmod = etree.SubElement(url, 'lastmod')
            lastmod.text = entry.lastmod.isoformat()

            changefreq = etree.SubElement(url, 'changefreq')
            changefreq.text = entry.changefreq

            priority = etree.SubElement(url, 'priority')
            priority.text = str(entry.priority)

        sitemap_file = File(f'{settings.DST_DIR}/{filename.format(i)}', type=FileType.BINARY)
        sitemap_file.contents = etree.tostring(urlset, encoding='utf-8', xml_declaration=True)
        if len(sitemap_file.contents) > settings.BLOG_SITEMAP_FILE_SIZE:
            raise JobError(f'The sitemap file is too big (> {settings.BLOG_SITEMAP_FILE_SIZE} bytes)')
        if settings.BLOG_SITEMAP_GZIP:
            sitemap_file.contents = gzip.compress(sitemap_file.contents, compresslevel=settings.GZIP_COMPRESS_LEVEL)
        sitemap_file.save()


def build_tags(template_engine: Optional[TemplateEngine] = None) -> None:
    """Create tag pages."""

    try:
        posts = context[settings.BLOG_CONTEXT_POSTS]
    except KeyError:
        raise JobError('No blog posts are found to build the tag pages')

    if template_engine is None:
        template_engine = JinjaTemplateEngine()

    tags = defaultdict(list)
    for post in posts:
        for tag in post.tags:
            tags[tag].append(post)
    tags = dict(sorted(tags.items()))

    tag_list = File(settings.BLOG_TAGS_DIR, settings.BLOG_INDEX_FILE)
    tag_list.contents = template_engine.render(
        settings.BLOG_TAG_LIST_TEMPLATE,
        {
            'context': context,
            'tags': tags,
            **settings,
        }
    )
    tag_list.save()

    add_sitemap_entry_to_context(f'{settings.BLOG_TAGS_URL}/')

    for tag, posts in tags.items():
        save_posts(posts, directory=f'{settings.BLOG_TAGS_DIR}/{tag.slug}',
                   template=settings.BLOG_TAG_DETAIL_TEMPLATE, template_engine=template_engine)
        add_sitemap_entry_to_context(f'{settings.BLOG_TAGS_URL}/{tag.slug}/')
