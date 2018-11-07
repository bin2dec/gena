"""Blog extension settings."""

from gena.contrib.blog.shortcuts import *
from gena.settings import settings
from gena.shortcuts import *
from gena.templating import JinjaTemplateEngine


# Assets dirs
BLOG_ASSETS_ROOT = getattr(settings, 'BLOG_ASSETS_ROOT', 'assets')
BLOG_CSS_ASSETS_DIR = getattr(settings, 'BLOG_CSS_ASSETS_DIR', f'{BLOG_ASSETS_ROOT}/css')
BLOG_IMAGES_ASSETS_DIR = getattr(settings, 'BLOG_IMAGES_ASSETS_DIR', f'{BLOG_ASSETS_ROOT}/images')
BLOG_JS_ASSETS_DIR = getattr(settings, 'BLOG_JS_ASSETS_DIR', f'{BLOG_ASSETS_ROOT}/js')

BLOG_ARCHIVE_DIR = getattr(settings, 'BLOG_ARCHIVE_DIR', 'archive')
BLOG_AUTHOR_ARCHIVE_DIR = getattr(settings, 'BLOG_AUTHOR_ARCHIVE_DIR', 'authors')
BLOG_CATEGORY_ARCHIVE_DIR = getattr(settings, 'BLOG_CATEGORY_ARCHIVE_DIR', 'categories')
BLOG_PAGES_DIR = getattr(settings, 'BLOG_PAGES_DIR', 'pages')
BLOG_POSTS_DIR = getattr(settings, 'BLOG_POSTS_DIR', 'posts')
BLOG_TAG_ARCHIVE_DIR = getattr(settings, 'BLOG_TAG_ARCHIVE_DIR', 'tags')


# Templates
BLOG_ARCHIVE_TEMPLATE = getattr(settings, 'BLOG_ARCHIVE_TEMPLATE', 'archive.html')
BLOG_MONTH_DETAIL_TEMPLATE = getattr(settings, 'BLOG_MONTH_DETAIL_TEMPLATE', 'month_detail.html')
BLOG_YEAR_DETAIL_TEMPLATE = getattr(settings, 'BLOG_YEAR_DETAIL_TEMPLATE', 'year_detail.html')

BLOG_AUTHOR_DETAIL_TEMPLATE = getattr(settings, 'BLOG_AUTHOR_DETAIL_TEMPLATE', 'author_detail.html')
BLOG_AUTHOR_LIST_TEMPLATE = getattr(settings, 'BLOG_AUTHOR_LIST_TEMPLATE', 'author_list.html')

BLOG_CATEGORY_DETAIL_TEMPLATE = getattr(settings, 'BLOG_CATEGORY_DETAIL_TEMPLATE', 'category_detail.html')
BLOG_CATEGORY_LIST_TEMPLATE = getattr(settings, 'BLOG_CATEGORY_LIST_TEMPLATE', 'category_list.html')

BLOG_MAIN_PAGE_TEMPLATE = getattr(settings, 'BLOG_MAIN_PAGE_TEMPLATE', 'main.html')

BLOG_PAGE_TEMPLATE = getattr(settings, 'BLOG_PAGE_TEMPLATE', 'page.html')
BLOG_POST_TEMPLATE = getattr(settings, 'BLOG_POST_TEMPLATE', 'post.html')

BLOG_TAG_DETAIL_TEMPLATE = getattr(settings, 'BLOG_TAG_DETAIL_TEMPLATE', 'tag_detail.html')
BLOG_TAG_LIST_TEMPLATE = getattr(settings, 'BLOG_TAG_LIST_TEMPLATE', 'tag_list.html')


# Context
BLOG_CONTEXT_PREFIX = getattr(settings, 'BLOG_CONTEXT_SECTION', 'blog_')
BLOG_CONTEXT_POSTS = getattr(settings, 'BLOG_CONTEXT_POSTS', f'{BLOG_CONTEXT_PREFIX}posts')


BLOG_TEASER_REGEXP = '<!--\s*more\s*-->'


# How many posts are displayed per page. When BLOG_POSTS_PER_PAGE=0, all posts are displayed
BLOG_POSTS_PER_PAGE = getattr(settings, 'BLOG_POSTS_PER_PAGE', 5)


_template_engine = JinjaTemplateEngine()


RULES = (
    {
        'test': f'{BLOG_CSS_ASSETS_DIR}/*.css',
        'processors': (
            save(path=f'{settings.DST_DIR}/{BLOG_CSS_ASSETS_DIR}/{{file.path.name}}'),
        ),
    },

    {
        'retest': 'favicon\.(gif|ico|jpe?g|png|svg)$',
        'processors': (
            save(path=f'{settings.DST_DIR}/favicon.ico'),
        ),
    },

    {
        'retest': f'{BLOG_IMAGES_ASSETS_DIR}/.*\.(bmp|gif|ico|jpe?g|png|svg|tiff?)$',
        'processors': (
            save(path=f'{settings.DST_DIR}/{BLOG_IMAGES_ASSETS_DIR}/{{file.path.name}}'),
        ),
    },

    {
        'test': f'{BLOG_JS_ASSETS_DIR}/*.js',
        'processors': (
            save(path=f'{settings.DST_DIR}/{BLOG_JS_ASSETS_DIR}/{{file.path.name}}'),
        ),
    },

    {
        'test': f'{BLOG_PAGES_DIR}/*.md',
        'processors': (
            markdown(),
            meta_date(),
            meta_modified(),
            meta_slug(),
            template(BLOG_PAGE_TEMPLATE, _template_engine),
            save(path=f'{settings.DST_DIR}/{BLOG_PAGES_DIR}/{{file.meta.slug}}/index.html'),
        ),
    },

    {
        'test': f'{BLOG_POSTS_DIR}/*.md',
        'processors': (
            markdown(),
            meta_date(),
            meta_modified(),
            meta_slug(),
            blog_post(_template_engine),
            save(path=f'{settings.DST_DIR}/{BLOG_POSTS_DIR}/{{file.meta.slug}}/index.html'),
        ),
    },
)


FINAL_JOBS = settings.FINAL_JOBS + (
    {
        'job': 'gena.contrib.blog.jobs.build_main_page',
        'options': {
            'template_engine': _template_engine,
        },
    },
)

if getattr(settings, 'BLOG_ARCHIVE', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_archive',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )

if getattr(settings, 'BLOG_AUTHOR_ARCHIVE', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_author_archive',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )

if getattr(settings, 'BLOG_CATEGORY_ARCHIVE', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_category_archive',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )

if getattr(settings, 'BLOG_TAG_ARCHIVE', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_tag_archive',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )
