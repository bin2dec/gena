"""GenA is a universal static site generator."""

import logging
import os.path
import sys
import sysconfig

from argparse import ArgumentParser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from time import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from gena import __version__
from gena import utils
from gena.context import context
from gena.settings import settings


logger = logging.getLogger(__name__)


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """Serves files from the current directory and below, directly mapping the directory structure to HTTP requests."""

    error_logging = False
    request_logging = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=settings.DST_DIR, **kwargs)

    def log_error(self, format, *args):
        """Logs an error when a request cannot be fulfilled."""
        if self.error_logging:
            super().log_error(format, *args)

    def log_message(self, format, *args):
        """Logs an arbitrary message."""
        logger.debug('%s', format % args)

    def log_request(self, code='-', size='-'):
        """Logs an accepted (successful) request."""
        if self.request_logging:
            super().log_request(code, size)


class SourceFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, runner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner = runner
        self.last_run = 0

    def on_any_event(self, event):
        if not event.is_directory and \
                self.runner.is_path_applicable(event.src_path) and \
                time() - self.last_run > settings.RERUN_INTERVAL:

            context.clear()
            self.runner.run()
            self.last_run = time()


class TemplateFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, runner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner = runner
        self.last_run = 0

    def on_modified(self, event):
        if not event.is_directory and \
                time() - self.last_run > settings.RERUN_INTERVAL:

            context.clear()
            self.runner.run()
            self.last_run = time()


def _build(args):
    """Build a project."""

    if args.src is not None:
        settings.SRC_DIR = args.src

    if args.dst is not None:
        settings.DST_DIR = args.dst

    runner = utils.import_attr(settings.RUNNER)
    start_time = time()
    runner = runner()
    files = runner.run()

    if not args.log_level == logging.CRITICAL:
        print(f'Finished in {time() - start_time:.2f} sec. with {len(files)} file(s) processed')


def _run(args):
    """Run a simple HTTP server to serve files from the destination directory."""

    if args.src is not None:
        settings.SRC_DIR = args.src

    if args.dst is not None:
        settings.DST_DIR = args.dst

    runner = utils.import_attr(settings.RUNNER)
    runner = runner()
    runner.run()

    if args.watch:
        source_file_handler = SourceFileSystemEventHandler(runner)
        template_file_handler = TemplateFileSystemEventHandler(runner)
        observer = Observer()
        observer.schedule(source_file_handler, settings.SRC_DIR, recursive=True)
        for extra_dir in settings.WATCHDOG_DIRS:
            observer.schedule(source_file_handler, extra_dir, recursive=True)
        for template_dir in settings.TEMPLATE_DIRS:
            observer.schedule(template_file_handler, template_dir, recursive=True)
        observer.start()
    else:
        observer = None

    if not args.log_level == logging.CRITICAL:
        print(f'Starting an HTTP server at http://{args.address}:{args.port}/\n'
              f'Press Ctrl-C to stop the server')

    with HTTPServer((args.address, args.port), HTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            if not args.log_level == logging.CRITICAL:
                print('Stopping the HTTP server')
            if observer:
                observer.stop()
                observer.join()


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

    run = subparsers.add_parser(
        'run',
        help='run a simple HTTP server to serve files from the destination directory',
    )

    run.add_argument(
        'src',
        help='the directory that contains source files (default: src)',
        metavar='source',
        nargs='?',
    )

    run.add_argument(
        'dst',
        help='the directory for processed files (default: dist)',
        metavar='destination',
        nargs='?',
    )

    run.add_argument(
        '-a', '--address',
        default='127.0.0.1',
        help='the address on which the server is listening (default: 127.0.0.1)',
    )

    run.add_argument(
        '-p', '--port',
        default=8000,
        help='the listening port (default: 8000)',
        type=int,
    )

    run.add_argument(
        '-w', '--watch',
        action='store_true',
        help='monitor the working directories recursively for changes and rerun the file processing if needed',
    )

    run.set_defaults(func=_run)

    try:
        args = parser.parse_args()

        if args.settings and os.path.exists(args.settings):
            settings.load_from_file(args.settings)

        if args.log_level == logging.DEBUG:
            settings.DEBUG = True

        log_config = utils.import_attr(settings.LOG_CONFIG)
        log_config(args.log_level)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('GenA %s', __version__)
            logger.debug('Python %s on %s', sysconfig.get_python_version(), sysconfig.get_platform())

        for extra_settings in settings.EXTRA_SETTINGS:
            logger.debug('Loading extra settings from "%s"', extra_settings)
            settings.load_from_module(extra_settings)

        args.func(args)
    except Exception as exception:
        logger.critical(exception)

        if settings.DEBUG:
            raise
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
