"""Default GenA settings."""

# The directory that contains source files.
SRC_DIR = 'src'

# The directory for processed files.
DST_DIR = 'dist'


DEBUG = False


# EXTRA_SETTINGS is a list of additional settings modules.
# For example:
# EXTRA_SETTINGS = ['gena.contrib.blog.settings']
EXTRA_SETTINGS = []


# TEMPLATE_DIRS contains a list of the paths to the templates.
TEMPLATE_DIRS = ['templates']


CACHE_DIR = ''


LANG = 'en'


RUNNER = 'gena.runners.FileRunner'


DEFAULT_FILE_FACTORY = 'gena.files.text_file'


# A default priority for processing tasks. A lower number means a higher priority.
DEFAULT_PRIORITY = 100


# JOBS
# Chains of callable objects, which are called one by one before and after the file processing.
# For example:
# FINAL_JOBS = [
#     ...
#     {
#         'job': 'gena.jobs.generate_file_from_template',
#         'options': {
#             'filename': 'articles.html',
#         },
#     },
#     ...
# ]

# Initial jobs are called before the file processing.
INITIAL_JOBS = []

# Final jobs are called after the file processing.
FINAL_JOBS = []


# See possible options http://jinja.pocoo.org/docs/api/#jinja2.Environment
JINJA_OPTIONS = {}


# See possible options https://python-markdown.github.io/reference/#markdown
# See the list of built-in extensions https://python-markdown.github.io/extensions/
MARKDOWN_OPTIONS = {
    'extensions': ['markdown.extensions.meta'],
    'output_format': 'html5',
}


# RULES is a list of rules to create processing tasks.
RULES = []


# See https://docs.python.org/3.7/library/subprocess.html#subprocess.run
EXTERNAL_PROCESSOR = {
    'check': True,
}


LOGGER_CONFIGURATOR = 'gena.log.config'
