DST_DIR = 'dist'


TEMPLATE_DIRS = ()


LANG = 'en'


RUNNER = 'gena.runners.FileRunner'


PROCESSING_RULES = ()


# See https://docs.python.org/3.7/library/subprocess.html#subprocess.run
EXTERNAL_PROCESSOR = {
    'check': True,
}


# See https://htmlmin.readthedocs.io/en/latest/reference.html#main-functions
HTML_MINIFIER_PROCESSOR_OPTIONS = {
    'remove_comments': True,
    'remove_empty_space': True,
    'reduce_boolean_attributes': True,
}


# See possible options http://jinja.pocoo.org/docs/api/#jinja2.Environment
JINJA2_PROCESSOR_OPTIONS = {
    'enable_async': True,
}


# See possible options https://python-markdown.github.io/reference/#markdown
# See the list of built-in extensions https://python-markdown.github.io/extensions/
MARKDOWN_PROCESSOR_OPTIONS = {
    'extensions': ['markdown.extensions.meta'],
    'output_format': 'html5',
}
