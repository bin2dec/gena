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
    'extensions': ['gena.md:SettingsExtension', 'markdown.extensions.meta'],
    'output_format': 'html5',
}


# RULES is a list of rules to create processing tasks.
RULES = []


# A dictionary of subprocess.run() arguments. It's primarily used by ExternalProcessor.
# See https://docs.python.org/3.7/library/subprocess.html#subprocess.run
EXTERNAL_PROCESSOR = {
    'check': True,
}


# A logging configuration function
LOG_CONFIG = 'gena.log.config'


# A minimal interval between two runs of the file processing.
RERUN_INTERVAL = 1  # sec


# A gzip compression level. It's is an integer from 0 to 9 controlling the level of compression;
# 1 is fastest and produces the least compression, and 9 is slowest and produces the most compression.
# 0 is no compression.
GZIP_COMPRESS_LEVEL = 9


# Visit directories pointed to by symlinks, on systems that support them.
# It's primarily used by FileRunner.
FOLLOW_SYMLINKS = False


# An additional list of directory paths that will be monitored.
# By default, only SRC_DIR and TEMPLATE_DIRS are monitored.
WATCHDOG_DIRS = []
