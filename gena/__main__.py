import logging
import os.path
import sysconfig

from argparse import ArgumentParser

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
        help='the directory that contains source files',
        metavar='source',
        nargs='?',
    )

    arg_parser.add_argument(
        'dst',
        help='the directory for processed files',
        metavar='destination',
        nargs='?',
    )

    arg_parser.add_argument(
        '-s', '--settings',
        default='settings.py',
        help='the settings of the application',
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

    arg_parser.set_defaults(log_level=logging.WARNING)

    args = arg_parser.parse_args()

    if args.settings and os.path.exists(args.settings):
        settings.load_from_module(args.settings)

    if args.src is not None:
        settings.SRC_DIR = args.src

    if args.dst is not None:
        settings.DST_DIR = args.dst

    if args.log_level == logging.DEBUG:
        settings.DEBUG = True

    logging.basicConfig(
        format=settings.DEBUG_LOG_FORMAT if settings.DEBUG else settings.LOG_FORMAT,
        level=args.log_level,
        style='{',
    )

    logger.debug(f'GenA {__version__}')
    logger.debug(f'Python {sysconfig.get_python_version()} on {sysconfig.get_platform()}')

    runner = utils.import_attr(settings.RUNNER)
    runner = runner()
    runner.run()


if __name__ == "__main__":
    main()
