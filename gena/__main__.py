import os.path

from argparse import ArgumentParser

from gena import __version__
from gena import utils
from gena.settings import settings


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
        '-v', '--version',
        action='version',
        version=__version__,
    )

    args = arg_parser.parse_args()

    if args.settings and os.path.exists(args.settings):
        settings.load_from_module(args.settings)

    if args.src is not None:
        settings.SRC_DIR = args.src

    if args.dst is not None:
        settings.DST_DIR = args.dst

    runner = utils.import_attr(settings.RUNNER)
    runner = runner()
    runner.run()


if __name__ == "__main__":
    main()
