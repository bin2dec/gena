from argparse import ArgumentParser

from gena import __version__
from gena import utils
from gena.settings import settings


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('src', nargs='?', default='src')
    arg_parser.add_argument('-s', '--settings')
    arg_parser.add_argument('-v', '--version', action='version', version=__version__)
    args = arg_parser.parse_args()

    if args.settings:
        settings.load_from_module(args.settings)

    runner = utils.import_attr(settings.RUNNER)
    runner = runner(args.src)
    runner.run()


if __name__ == "__main__":
    main()
