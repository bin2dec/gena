import logging
import os.path
import sys
import sysconfig

from argparse import ArgumentParser
from time import time

from gena import __version__
from gena import utils
from gena.settings import settings


logger = logging.getLogger(__name__)


def _build(args):
    if args.src is not None:
        settings.SRC_DIR = args.src

    if args.dst is not None:
        settings.DST_DIR = args.dst

    try:
        runner = utils.import_attr(settings.RUNNER)
        start_time = time()
        runner = runner()
        files = runner.run()
    except Exception as exception:
        logger.critical(exception)

        if settings.DEBUG:
            raise
        else:
            sys.exit(1)
    else:
        if not args.log_level == logging.CRITICAL:
            print(f'Finished in {time() - start_time:.2f} sec. with {files} file(s) processed')


def main():
    parser = ArgumentParser(
        'gena',
        description='A universal static site generator',
    )

    parser.add_argument(
        '-s', '--settings',
        default='settings.py',
        help='the settings of the application (default: settings.py)',
    )

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=__version__,
    )

    log_level = parser.add_mutually_exclusive_group()

    log_level.add_argument(
        '-q', '--quiet',
        action='store_const',
        const=logging.CRITICAL,
        dest='log_level',
        help='show only critical errors',
    )

    log_level.add_argument(
        '-v', '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='log_level',
        help='show all messages except debug ones',
    )

    log_level.add_argument(
        '-d', '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='log_level',
        help='show all messages'
    )

    parser.add_argument(
        '--show-settings',
        action='store_true',
        help='show the settings',
    )

    subparsers = parser.add_subparsers(
        dest='command',
        required=True,
        title='commands',
    )

    build = subparsers.add_parser(
        'build',
        help='build a project',
    )

    build.add_argument(
        'src',
        help='the directory that contains source files (default: src)',
        metavar='source',
        nargs='?',
    )

    build.add_argument(
        'dst',
        help='the directory for processed files (default: dist)',
        metavar='destination',
        nargs='?',
    )

    build.set_defaults(func=_build)

    args = parser.parse_args()

    if args.settings and os.path.exists(args.settings):
        settings.load_from_file(args.settings)

    if args.log_level == logging.DEBUG:
        settings.DEBUG = True

    log_config = utils.import_attr(settings.LOGGER_CONFIGURATOR)
    log_config(args.log_level)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('GenA %s', __version__)
        logger.debug('Python %s on %s', sysconfig.get_python_version(), sysconfig.get_platform())

    for extra_settings in settings.EXTRA_SETTINGS:
        logger.debug('Loading extra settings from "%s"', extra_settings)
        settings.load_from_module(extra_settings)

    args.func(args)


if __name__ == '__main__':
    main()
