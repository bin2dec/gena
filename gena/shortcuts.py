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
    'cssmin',
    'filename',
    'group',
    'markdown',
    'meta_date',
    'meta_modified',
    'meta_slug',
    'save',
    'stdout',
    'template',
    'uglifyjs',
)


def bundle(name):
    return {
        'processor': 'gena.processors.BundleProcessor',
        'options': {
            'name': name,
        },
    }


def cssmin(*args):
    """You need to install cssmin to use this shortcut: https://github.com/jbleuzen/node-cssmin#installation."""

    if not args:
        args = ('cssmin',)

    return {
        'processor': 'gena.processors.ExternalProcessor',
        'options': {
            'command': args,
        },
    }


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


def save(append=False, path=''):
    return {
        'processor': 'gena.processors.SavingProcessor',
        'options': {
            'append': append,
            'path': path,
        },
    }


def stdout():
    return {'processor': 'gena.processors.StdoutProcessor'}


def template(name, engine=None):
    return {
        'processor': 'gena.processors.TemplateProcessor',
        'options': {
            'template': name,
            'engine': engine,
        },
    }


def uglifyjs(*args):
    """You need to install UglifyJS to use this shortcut: https://github.com/mishoo/UglifyJS2#install."""

    if not args:
        args = ('uglifyjs', '-c', '-m')

    return {
        'processor': 'gena.processors.ExternalProcessor',
        'options': {
            'command': args,
        },
    }
