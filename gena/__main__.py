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


def main():
    arg_parser = ArgumentParser(
        'gena',
        description='A universal static site generator',
    )

    arg_parser.add_argument(
        'src',
        help='the directory that contains source files (default: src)',
        metavar='source',
        nargs='?',
    )

    arg_parser.add_argument(
        'dst',
        help='the directory for processed files (default: dist)',
        metavar='destination',
        nargs='?',
    )

    arg_parser.add_argument(
        '-s', '--settings',
        default='settings.py',
        help='the settings of the application (default: settings.py)',
    )

    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version=__version__,
    )

    log_level_group = arg_parser.add_mutually_exclusive_group()

    log_level_group.add_argument(
        '-q', '--quiet',
        action='store_const',
        const=logging.CRITICAL,
        dest='log_level',
        help='show only critical errors',
    )

    log_level_group.add_argument(
        '-v', '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='log_level',
        help='show all messages except debug ones',
    )

    log_level_group.add_argument(
        '-d', '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='log_level',
        help='show all messages'
    )

    arg_parser.add_argument(
        '--show-settings',
        action='store_true',
        help='show the settings',
    )

    args = arg_parser.parse_args()

    if args.settings and os.path.exists(args.settings):
        settings.load_from_file(args.settings)

    if args.src is not None:
        settings.SRC_DIR = args.src

    if args.dst is not None:
        settings.DST_DIR = args.dst

    if args.log_level == logging.DEBUG:
        settings.DEBUG = True

    log_config = utils.import_attr(settings.LOGGER_CONFIGURATOR)
    log_config(args.log_level)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('GenA %s', __version__)
        logger.debug('Python %s on %s', sysconfig.get_python_version(), sysconfig.get_platform())

    if args.show_settings:
        print(settings)

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


if __name__ == "__main__":
    main()
