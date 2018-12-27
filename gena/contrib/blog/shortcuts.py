"""This module contains various shortcuts for creating processor rules more easily."""

__all__ = (
    'blog_post',
    'sitemap',
)


def blog_post(template_engine=None):
    return {
        'processor': 'gena.contrib.blog.processors.BlogPostProcessor',
        'options': {
            'template_engine': template_engine,
        },
    }


def sitemap(loc):
    return {
        'processor': 'gena.contrib.blog.processors.SitemapProcessor',
        'options': {
            'loc': loc,
        },
    }
