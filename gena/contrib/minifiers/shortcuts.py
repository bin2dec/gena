"""This module contains various shortcuts for creating processor rules more easily."""

__all__ = (
    'html_minifier',
)


def html_minifier():
    return {'processor': 'gena.contrib.minifiers.processors.HTMLMinifierProcessor'}
