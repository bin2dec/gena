"""
This module contains various shortcuts for creating processor rules more easily.
"""

from gena import utils
from slugify import slugify


__all__ = (
    'filename',
    'group',
    'html_minifier',
    'markdown',
    'meta_date',
    'meta_modified',
    'meta_slug',
    'save',
    'template',
)


def filename(name):
    return {
        'processor': 'gena.processors.FileNameProcessor',
        'options': {
            'name': name,
        },
    }


def group(name):
    return {
        'processor': 'gena.processors.GroupProcessor',
        'options': {
            'name': name,
        },
    }


def html_minifier():
    return {'processor': 'gena.processors.HTMLMinifierProcessor'}


def markdown():
    return {'processor': 'gena.processors.MarkdownProcessor'}


def meta_date():
    return {
        'processor': 'gena.processors.FileMetaProcessor',
        'options': {
            'key': 'date',
            'callback': utils.get_datetime,
        },
    }


def meta_modified():
    return {
        'processor': 'gena.processors.FileMetaProcessor',
        'options': {
            'key': 'modified',
            'callback': utils.get_datetime,
            'default': lambda file: [file.mtime],
        },
    }


def meta_slug():
    return {
        'processor': 'gena.processors.FileMetaProcessor',
        'options': {
            'key': 'slug',
            'callback': slugify,
            'default': lambda file: file.meta.title,
            'skip_if_exists': True,
        },
    }


def save():
    return {'processor': 'gena.processors.SavingProcessor'}


def template(name):
    return {
        'processor': 'gena.processors.TemplateProcessor',
        'options': {
            'template': name,
        },
    }
