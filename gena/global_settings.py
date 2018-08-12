DST_DIR = 'dist'


TEMPLATE_DIRS = ()


LANG = 'en'


RUNNER = 'gena.runners.FileRunner'


FILE = 'gena.files.File'


# JOBS
# Chains of callable objects, which are called one by one before and after the file processing.
# For example:
# FINAL_JOBS = (
#     ...
#     {
#         'job': 'gena.jobs.generate_file_from_template',
#         'options': {
#             'filename': 'articles.html',
#         },
#     },
#     ...
# )

# Initial jobs are called before the file processing
INITIAL_JOBS = ()

# Final jobs are called after the file processing
FINAL_JOBS = ()


# See possible options https://htmlmin.readthedocs.io/en/latest/reference.html#main-functions
HTML_MINIFIER_OPTIONS = {
    'remove_comments': True,
    'remove_empty_space': True,
    'reduce_boolean_attributes': True,
}


# See possible options http://jinja.pocoo.org/docs/api/#jinja2.Environment
JINJA2_OPTIONS = {
    'enable_async': True,
}


PROCESSING_RULES = ()


# See https://docs.python.org/3.7/library/subprocess.html#subprocess.run
EXTERNAL_PROCESSOR = {
    'check': True,
}


# See possible options https://python-markdown.github.io/reference/#markdown
# See the list of built-in extensions https://python-markdown.github.io/extensions/
MARKDOWN_PROCESSOR_OPTIONS = {
    'extensions': ['markdown.extensions.meta'],
    'output_format': 'html5',
}
