"""Minifiers extension settings."""

from gena.settings import settings


# See possible options https://htmlmin.readthedocs.io/en/latest/reference.html#main-functions
DEFAULT_HTML_MINIFIER_OPTIONS = {
    'reduce_boolean_attributes': True,
    'remove_comments': True,
    'remove_empty_space': True,
}

HTML_MINIFIER_OPTIONS = settings.get('HTML_MINIFIER_OPTIONS', DEFAULT_HTML_MINIFIER_OPTIONS)
