"""This module contains various shortcuts for creating processor rules more easily."""

__all__ = (
    'blog_post',
)


def blog_post(contents=False):
    return {
        'processor': 'gena.contrib.blog.processors.BlogPostProcessor',
        'options': {
            'contents': contents,
        },
    }