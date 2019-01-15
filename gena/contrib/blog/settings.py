"""Blog extension settings."""

import logging

from gena.contrib.blog.shortcuts import *
from gena.settings import settings
from gena.shortcuts import *
from gena.templating import JinjaTemplateEngine


logger = logging.getLogger(__name__)


BLOG_ASSETS = getattr(settings, 'BLOG_ASSETS', 'assets')
BLOG_CSS_ASSETS = getattr(settings, 'BLOG_CSS_ASSETS', f'{BLOG_ASSETS}/css')
BLOG_FONTS_ASSETS = getattr(settings, 'BLOG_FONTS_ASSETS', f'{BLOG_ASSETS}/fonts')
BLOG_IMAGES_ASSETS = getattr(settings, 'BLOG_IMAGES_ASSETS', f'{BLOG_ASSETS}/images')
BLOG_JS_ASSETS = getattr(settings, 'BLOG_JS_ASSETS', f'{BLOG_ASSETS}/js')
BLOG_SASS_ASSETS = getattr(settings, 'BLOG_SASS_ASSETS', f'{BLOG_ASSETS}/sass')

BLOG_ARCHIVE = getattr(settings, 'BLOG_ARCHIVE', 'archive')
BLOG_AUTHORS = getattr(settings, 'BLOG_AUTHORS', 'authors')
BLOG_CATEGORIES = getattr(settings, 'BLOG_CATEGORIES', 'categories')
BLOG_PAGES = getattr(settings, 'BLOG_PAGES', 'pages')
BLOG_POSTS = getattr(settings, 'BLOG_POSTS', 'posts')
BLOG_TAGS = getattr(settings, 'BLOG_TAGS', 'tags')


# Assets dirs
BLOG_CSS_ASSETS_DIR = getattr(settings, 'BLOG_CSS_ASSETS_DIR', f'{settings.DST_DIR}/{BLOG_CSS_ASSETS}')
BLOG_FONTS_ASSETS_DIR = getattr(settings, 'BLOG_FONTS_ASSETS_DIR', f'{settings.DST_DIR}/{BLOG_FONTS_ASSETS}')
BLOG_IMAGES_ASSETS_DIR = getattr(settings, 'BLOG_IMAGES_ASSETS_DIR', f'{settings.DST_DIR}/{BLOG_IMAGES_ASSETS}')
BLOG_JS_ASSETS_DIR = getattr(settings, 'BLOG_JS_ASSETS_DIR', f'{settings.DST_DIR}/{BLOG_JS_ASSETS}')
BLOG_SASS_ASSETS_DIR = getattr(settings, 'BLOG_SASS_ASSETS_DIR', f'{settings.DST_DIR}/{BLOG_SASS_ASSETS}')

BLOG_ARCHIVE_DIR = getattr(settings, 'BLOG_ARCHIVE_DIR', f'{settings.DST_DIR}/{BLOG_ARCHIVE}')
BLOG_AUTHORS_DIR = getattr(settings, 'BLOG_AUTHORS_DIR', f'{settings.DST_DIR}/{BLOG_AUTHORS}')
BLOG_CATEGORIES_DIR = getattr(settings, 'BLOG_CATEGORIES_DIR', f'{settings.DST_DIR}/{BLOG_CATEGORIES}')
BLOG_PAGES_DIR = getattr(settings, 'BLOG_PAGES_DIR', f'{settings.DST_DIR}/{BLOG_PAGES}')
BLOG_POSTS_DIR = getattr(settings, 'BLOG_POSTS_DIR', f'{settings.DST_DIR}/{BLOG_POSTS}')
BLOG_TAGS_DIR = getattr(settings, 'BLOG_TAGS_DIR', f'{settings.DST_DIR}/{BLOG_TAGS}')


# URLs
BLOG_URL = getattr(settings, 'BLOG_URL', '')  # should be the full URL, including the protocol (e.g. http, https)

BLOG_CSS_URL = getattr(settings, 'BLOG_CSS_URL', f'{BLOG_URL}/{BLOG_CSS_ASSETS}')
BLOG_FONTS_URL = getattr(settings, 'BLOG_FONTS_URL', f'{BLOG_URL}/{BLOG_FONTS_ASSETS}')
BLOG_IMAGES_URL = getattr(settings, 'BLOG_IMAGES_URL', f'{BLOG_URL}/{BLOG_IMAGES_ASSETS}')
BLOG_JS_URL = getattr(settings, 'BLOG_JS_URL', f'{BLOG_URL}/{BLOG_JS_ASSETS}')

BLOG_ARCHIVE_URL = getattr(settings, 'BLOG_ARCHIVE_URL', f'{BLOG_URL}/{BLOG_ARCHIVE}')
BLOG_AUTHORS_URL = getattr(settings, 'BLOG_AUTHORS_URL', f'{BLOG_URL}/{BLOG_AUTHORS}')
BLOG_CATEGORIES_URL = getattr(settings, 'BLOG_CATEGORIES_URL', f'{BLOG_URL}/{BLOG_CATEGORIES}')
BLOG_PAGES_URL = getattr(settings, 'BLOG_PAGES_URL', f'{BLOG_URL}/{BLOG_PAGES}')
BLOG_POSTS_URL = getattr(settings, 'BLOG_POSTS_URL', f'{BLOG_URL}/{BLOG_POSTS}')
BLOG_TAGS_URL = getattr(settings, 'BLOG_TAGS_URL', f'{BLOG_URL}/{BLOG_TAGS}')


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
BLOG_CONTEXT_SITEMAP = getattr(settings, 'BLOG_CONTEXT_SITEMAP', f'{BLOG_CONTEXT_PREFIX}sitemap')


BLOG_TEASER_REGEXP = getattr(settings, 'BLOG_TEASER_REGEXP', r'<!--\s*more\s*-->')


# How many posts are displayed per page. When BLOG_POSTS_PER_PAGE=0, all posts are displayed
BLOG_POSTS_PER_PAGE = getattr(settings, 'BLOG_POSTS_PER_PAGE', 5)


BLOG_INDEX_FILE = getattr(settings, 'BLOG_INDEX_FILE', 'index.html')
BLOG_N_INDEX_FILE = getattr(settings, 'BLOG_N_INDEX_FILE', 'index{}.html')


BLOG_SITEMAP = getattr(settings, 'BLOG_SITEMAP', False)

BLOG_SITEMAP_SCHEMA = getattr(settings, 'BLOG_SITEMAP_SCHEMA', 'http://www.sitemaps.org/schemas/sitemap/0.9')

BLOG_SITEMAP_FILENAME = getattr(settings, 'BLOG_SITEMAP_FILENAME', 'sitemap.xml')
BLOG_N_SITEMAP_FILENAME = getattr(settings, 'BLOG_N_SITEMAP_FILENAME', 'sitemap{}.xml')

BLOG_SITEMAP_SIZE = getattr(settings, 'BLOG_SITEMAP_SIZE', 50_000)  # records
BLOG_SITEMAP_FILE_SIZE = getattr(settings, 'BLOG_SITEMAP_FILE_SIZE', 1_048_576)  # bytes

BLOG_SITEMAP_LOC_SIZE = getattr(settings, 'BLOG_SITEMAP_LOC_SIZE', 2_048)  # characters
BLOG_SITEMAP_CHANGEFREQ_LIST = getattr(settings, 'BLOG_SITEMAP_CHANGEFREQ_LIST', ['always', 'hourly', 'daily', 'weekly',
                                                                                  'monthly', 'yearly', 'never'])
BLOG_SITEMAP_PRIORITY_RANGE = getattr(settings, 'BLOG_SITEMAP_PRIORITY_RANGE', [0.0, 1.0])

BLOG_SITEMAP_DEFAULT_CHANGEFREQ = getattr(settings, 'BLOG_SITEMAP_DEFAULT_CHANGEFREQ', 'monthly')
BLOG_SITEMAP_DEFAULT_PRIORITY = getattr(settings, 'BLOG_SITEMAP_DEFAULT_PRIORITY', 0.5)

BLOG_SITEMAP_META_PREFIX = getattr(settings, 'BLOG_SITEMAP_META_PREFIX', 'sitemap-')

BLOG_SITEMAP_GZIP = getattr(settings, 'BLOG_SITEMAP_GZIP', False)

if BLOG_SITEMAP and not BLOG_URL:
    logger.warning('The BLOG_URL setting is needed to create a proper "sitemap.xml" but it\'s empty. '
                   'So either disable the sitemap creating (BLOG_SITEMAP=False) or fill BLOG_URL')
    BLOG_SITEMAP = False


_template_engine = JinjaTemplateEngine()


RULES = settings.RULES + [
    {
        'retest': r'/favicon\.(gif|ico|jpe?g|png|svg)$',
        'processors': (
            save(path=f'{settings.DST_DIR}/favicon.ico'),
        ),
    },

    {
        'retest': fr'/{BLOG_IMAGES_ASSETS}/.*\.(bmp|gif|ico|jpe?g|png|svg|tiff?)$',
        'processors': (
            save(path=f'{BLOG_IMAGES_ASSETS_DIR}/{{file.path.name}}'),
        ),
    },

    {
        'test': f'/{BLOG_PAGES}/*.md',
        'processors': (
            markdown(),
            meta_date(),
            meta_modified(),
            meta_slug(),
            template(BLOG_PAGE_TEMPLATE, _template_engine),
            sitemap(f'{BLOG_PAGES_URL}/{{file.meta.slug}}/') if BLOG_SITEMAP else None,
            save(path=f'{BLOG_PAGES_DIR}/{{file.meta.slug}}/{BLOG_INDEX_FILE}'),
        ),
    },

    {
        'test': f'/{BLOG_POSTS}/*.md',
        'processors': (
            markdown(),
            meta_date(),
            meta_modified(),
            meta_slug(),
            blog_post(_template_engine),
            save(path=f'{BLOG_POSTS_DIR}/{{file.meta.slug}}/index.html'),
        ),
    },

    {
        'retest': fr'/{BLOG_FONTS_ASSETS}/.*\.(eot|svg|ttf|woff\d)$',
        'processors': (
            save(path=f'{BLOG_FONTS_ASSETS_DIR}/{{file.path.name}}'),
        ),
    },

    {
        'test': '/robots.txt',
        'processors': (
            save(path=f'{settings.DST_DIR}/robots.txt'),
        ),
    },
]

if getattr(settings, 'BLOG_CSS_MIN', False):
    RULES += [
        {
            'test': f'/{BLOG_CSS_ASSETS}/*.min.css',
            'processors': (
                save(path=f'{BLOG_CSS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },

        {
            'test': f'/{BLOG_CSS_ASSETS}/*.css',
            'processors': (
                cssmin(),
                save(path=f'{BLOG_CSS_ASSETS_DIR}/{{file.path.basename}}.min{{file.path.extension}}'),
            ),
        },

        {
            'retest': fr'/{BLOG_SASS_ASSETS}/(.*/)?[^_][^/]*\.(sass|scss)*$',
            'processors': (
                sass(),
                save(path=f'{BLOG_CSS_ASSETS_DIR}/{{file.path.basename}}.min.css'),
            ),
        },
    ]
else:
    RULES += [
        {
            'test': f'/{BLOG_CSS_ASSETS}/*.css',
            'processors': (
                save(path=f'{BLOG_CSS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },

        {
            'retest': fr'/{BLOG_SASS_ASSETS}/(.*/)?[^_][^/]*\.(sass|scss)*$',
            'processors': (
                sass(args=('sass', '--stdin')),
                save(path=f'{BLOG_CSS_ASSETS_DIR}/{{file.path.basename}}.css'),
            ),
        },
    ]

if getattr(settings, 'BLOG_JS_MIN', False):
    RULES += [
        {
            'test': f'/{BLOG_JS_ASSETS}/*.min.js',
            'processors': (
                save(path=f'{BLOG_JS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },

        {
            'test': f'/{BLOG_JS_ASSETS}/*.js',
            'processors': (
                uglifyjs(),
                save(path=f'{BLOG_JS_ASSETS_DIR}/{{file.path.basename}}.min{{file.path.extension}}'),
            ),
        },
    ]
else:
    RULES.append(
        {
            'test': f'/{BLOG_JS_ASSETS}/*.js',
            'processors': (
                save(path=f'{BLOG_JS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },
    )


INITIAL_JOBS = [
    {'job': 'gena.jobs.clear_dst_dir'},
]


FINAL_JOBS = settings.FINAL_JOBS + [
    {
        'job': 'gena.contrib.blog.jobs.build_main_page',
        'options': {
            'template_engine': _template_engine,
        },
    },
]

if getattr(settings, 'BLOG_ARCHIVE', True):
    FINAL_JOBS += [
        {
            'job': 'gena.contrib.blog.jobs.build_archive',
            'options': {
                'template_engine': _template_engine,
            },
        },
    ]

if getattr(settings, 'BLOG_AUTHORS', True):
    FINAL_JOBS += [
        {
            'job': 'gena.contrib.blog.jobs.build_authors',
            'options': {
                'template_engine': _template_engine,
            },
        },
    ]

if getattr(settings, 'BLOG_CATEGORIES', True):
    FINAL_JOBS += [
        {
            'job': 'gena.contrib.blog.jobs.build_categories',
            'options': {
                'template_engine': _template_engine,
            },
        },
    ]

if getattr(settings, 'BLOG_TAGS', True):
    FINAL_JOBS += [
        {
            'job': 'gena.contrib.blog.jobs.build_tags',
            'options': {
                'template_engine': _template_engine,
            },
        },
    ]

# The build_sitemap job should be the last final job
if BLOG_SITEMAP:
    FINAL_JOBS += [
        {'job': 'gena.contrib.blog.jobs.build_sitemap'},
    ]
