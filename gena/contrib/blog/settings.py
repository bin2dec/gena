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


BLOG_PAGES_DIR = getattr(settings, 'BLOG_PAGES_DIR', 'pages')
BLOG_POSTS_DIR = getattr(settings, 'BLOG_POSTS_DIR', 'posts')


# Templates
BLOG_MAIN_PAGE_TEMPLATE = getattr(settings, 'BLOG_MAIN_PAGE_TEMPLATE', 'main.html')

BLOG_PAGE_TEMPLATE = getattr(settings, 'BLOG_PAGE_TEMPLATE', 'page.html')
BLOG_POST_TEMPLATE = getattr(settings, 'BLOG_POST_TEMPLATE', 'post.html')


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
            blog_post(),
            template(BLOG_POST_TEMPLATE, _template_engine),
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
