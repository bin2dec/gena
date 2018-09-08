"""
This module contains various shortcuts for creating processor rules more easily.
Let's take a look at the difference between two sets of rules:

1) Rules without shortcuts
RULES = (
    {
        'test': '*.md',
        'processors': (
            {'processor': 'gena.processors.MarkdownProcessor'},
            {
                'processor': 'gena.processors.TemplateProcessor',
                'options': {
                    'template': 'index.html',
                },
            },
            {
                'processor': 'gena.processors.FileNameProcessor',
                'options': {
                    'name': 'index.html',
                },
            },
            {'processor': 'gena.processors.SavingProcessor'},
        ),
    },
)

2) The same rules but with shortcuts
RULES = (
    {
        'test': '*.md',
        'processors': (
            markdown(),
            template('index.html'),
            filename('index.html'),
            save(),
        ),
    },
)
"""

from slugify import slugify

from gena import utils


__all__ = (
    'bundle',
    'filename',
    'group',
    'html_minifier',
    'markdown',
    'meta_date',
    'meta_modified',
    'meta_slug',
    'save',
    'stdout',
    'template',
)


def bundle(name):
    return {
        'processor': 'gena.processors.BundleProcessor',
        'options': {
            'name': name,
        },
    },


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


def stdout():
    return {'processor': 'gena.processors.StdoutProcessor'}


def template(name):
    return {
        'processor': 'gena.processors.TemplateProcessor',
        'options': {
            'template': name,
        },
    }