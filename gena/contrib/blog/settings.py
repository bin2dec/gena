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
BLOG_SASS_ASSETS_DIR = getattr(settings, 'BLOG_SASS_ASSETS_DIR', f'{BLOG_ASSETS_ROOT}/sass')

BLOG_ARCHIVE_DIR = getattr(settings, 'BLOG_ARCHIVE_DIR', 'archive')
BLOG_AUTHORS_DIR = getattr(settings, 'BLOG_AUTHORS_DIR', 'authors')
BLOG_CATEGORIES_DIR = getattr(settings, 'BLOG_CATEGORIES_DIR', 'categories')
BLOG_PAGES_DIR = getattr(settings, 'BLOG_PAGES_DIR', 'pages')
BLOG_POSTS_DIR = getattr(settings, 'BLOG_POSTS_DIR', 'posts')
BLOG_TAGS_DIR = getattr(settings, 'BLOG_TAGS_DIR', 'tags')


# URLs
BLOG_URL = getattr(settings, 'BLOG_URL', '')

BLOG_CSS_URL = getattr(settings, 'BLOG_CSS_URL', f'{BLOG_URL}/{BLOG_CSS_ASSETS_DIR}')
BLOG_IMAGES_URL = getattr(settings, 'BLOG_IMAGES_URL', f'{BLOG_URL}/{BLOG_IMAGES_ASSETS_DIR}')
BLOG_JS_URL = getattr(settings, 'BLOG_JS_URL', f'{BLOG_URL}/{BLOG_JS_ASSETS_DIR}')

BLOG_AUTHORS_URL = getattr(settings, 'BLOG_AUTHORS_URL', f'{BLOG_URL}/{BLOG_AUTHORS_DIR}')
BLOG_CATEGORIES_URL = getattr(settings, 'BLOG_CATEGORIES_URL', f'{BLOG_URL}/{BLOG_CATEGORIES_DIR}')
BLOG_PAGES_URL = getattr(settings, 'BLOG_PAGES_URL', f'{BLOG_URL}/{BLOG_PAGES_DIR}')
BLOG_POSTS_URL = getattr(settings, 'BLOG_POSTS_URL', f'{BLOG_URL}/{BLOG_POSTS_DIR}')
BLOG_TAGS_URL = getattr(settings, 'BLOG_TAGS_URL', f'{BLOG_URL}/{BLOG_TAGS_DIR}')


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


BLOG_TEASER_REGEXP = r'<!--\s*more\s*-->'


# How many posts are displayed per page. When BLOG_POSTS_PER_PAGE=0, all posts are displayed
BLOG_POSTS_PER_PAGE = getattr(settings, 'BLOG_POSTS_PER_PAGE', 5)


_template_engine = JinjaTemplateEngine()


RULES = settings.RULES + [
    {
        'retest': r'favicon\.(gif|ico|jpe?g|png|svg)$',
        'processors': (
            save(path=f'{settings.DST_DIR}/favicon.ico'),
        ),
    },

    {
        'retest': fr'{BLOG_IMAGES_ASSETS_DIR}/.*\.(bmp|gif|ico|jpe?g|png|svg|tiff?)$',
        'processors': (
            save(path=f'{settings.DST_DIR}/{BLOG_IMAGES_ASSETS_DIR}/{{file.path.name}}'),
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
]

if getattr(settings, 'BLOG_CSS_MIN', False):
    RULES += [
        {
            'test': f'{BLOG_CSS_ASSETS_DIR}/*.min.css',
            'processors': (
                save(path=f'{settings.DST_DIR}/{BLOG_CSS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },

        {
            'test': f'{BLOG_CSS_ASSETS_DIR}/*.css',
            'processors': (
                cssmin(),
                save(path=f'{settings.DST_DIR}/{BLOG_CSS_ASSETS_DIR}/'
                          f'{{file.path.basename}}.min{{file.path.extension}}'),
            ),
        },

        {
            'retest': fr'{BLOG_SASS_ASSETS_DIR}/(.*/)?[^_][^/]*\.(sass|scss)*$',
            'processors': (
                sass(),
                save(path=f'{settings.DST_DIR}/{BLOG_CSS_ASSETS_DIR}/{{file.path.basename}}.min.css'),
            ),
        },
    ]
else:
    RULES += [
        {
            'test': f'{BLOG_CSS_ASSETS_DIR}/*.css',
            'processors': (
                save(path=f'{settings.DST_DIR}/{BLOG_CSS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },

        {
            'retest': fr'{BLOG_SASS_ASSETS_DIR}/(.*/)?[^_][^/]*\.(sass|scss)*$',
            'processors': (
                sass(args=('sass', '--stdin')),
                save(path=f'{settings.DST_DIR}/{BLOG_CSS_ASSETS_DIR}/{{file.path.basename}}.css'),
            ),
        },
    ]

if getattr(settings, 'BLOG_JS_MIN', False):
    RULES += [
        {
            'test': f'{BLOG_JS_ASSETS_DIR}/*.min.js',
            'processors': (
                save(path=f'{settings.DST_DIR}/{BLOG_JS_ASSETS_DIR}/{{file.path.name}}'),
            ),
        },

        {
            'test': f'{BLOG_JS_ASSETS_DIR}/*.js',
            'processors': (
                uglifyjs(),
                save(path=f'{settings.DST_DIR}/{BLOG_JS_ASSETS_DIR}/'
                          f'{{file.path.basename}}.min{{file.path.extension}}'),
            ),
        },
    ]
else:
    RULES.append(
        {
            'test': f'{BLOG_JS_ASSETS_DIR}/*.js',
            'processors': (
                save(path=f'{settings.DST_DIR}/{BLOG_JS_ASSETS_DIR}/{{file.path.name}}'),
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

if getattr(settings, 'BLOG_AUTHORS', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_authors',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )

if getattr(settings, 'BLOG_CATEGORIES', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_categories',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )

if getattr(settings, 'BLOG_TAGS', True):
    FINAL_JOBS += (
        {
            'job': 'gena.contrib.blog.jobs.build_tags',
            'options': {
                'template_engine': _template_engine,
            },
        },
    )
