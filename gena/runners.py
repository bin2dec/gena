import heapq
import itertools
import logging
import os

from fnmatch import fnmatch
from typing import Iterable

from gena import utils
from gena.settings import settings
from gena.utils import map_as_kwargs


__all__ = (
    'FileRunner',
)


logger = logging.getLogger(__name__)


def do_jobs(jobs: Iterable):
    """Do jobs from the given list.

    A job is a special callable object that can be called before or after the file processing.
    An example of a valid job list (can be declared in your settings):

    INITIAL_JOBS = (
        {'job': 'gena.jobs.clear_dst_dir'},
    )
    """

    for job in jobs:
        obj = job['job']
        if not callable(obj):
            obj = utils.import_attr(obj)
        options = job.get('options', {})
        logger.debug(f'Doing the {obj.__name__}({map_as_kwargs(options)}) job')
        obj(**options)


def do_initial_jobs():
    """Initial jobs are called before the file processing."""
    logger.debug('Doing the initial jobs')
    do_jobs(settings.INITIAL_JOBS)


def do_final_jobs():
    """Final jobs are called after the file processing."""
    logger.debug('Doing the final jobs')
    do_jobs(settings.FINAL_JOBS)


class FileRunner:
    def __init__(self):
        default_file_factory = utils.import_attr(settings.DEFAULT_FILE_FACTORY)
        default_file_factory = default_file_factory()

        try:
            rules = settings.RULES
        except AttributeError:
            rules = settings.PROCESSING_RULES

        self._rules = []
        for rule in rules:
            new_processors = []
            for processor in rule['processors']:
                new_processor = utils.import_attr(processor['processor'])
                new_processor = new_processor(**processor.get('options', {}))
                new_processors.append(new_processor)

            if 'file_factory' in rule:
                file_factory = utils.import_attr(rule['file_factory'])
                file_factory = file_factory()
            else:
                file_factory = default_file_factory

            new_rule = {
                'test': rule['test'],
                'processors': new_processors,
                'file_factory': file_factory,
                'priority': rule.get('priority', settings.DEFAULT_PRIORITY)
            }
            self._rules.append(new_rule)

    def _get_paths(self):
        for dirpath, _, filenames in os.walk(settings.SRC_DIR):
            for filename in filenames:
                yield (dirpath, filename)

    def _get_rule(self, test):
        for rule in self._rules:
            if fnmatch(test, rule['test']):
                return rule

    def _get_tasks(self):
        counter = itertools.count()  # the counter is needed in situations when priorities are equal
        queue = []

        for dirpath, filename in self._get_paths():
            rule = self._get_rule(filename)
            path = os.path.join(dirpath, filename)
            if rule:
                file = rule['file_factory'](path)
                task = (file, rule['processors'])
                entry = (rule['priority'], next(counter), task)
                heapq.heappush(queue, entry)
                logger.debug(f'Created a task for "{file.path}" with priority={rule["priority"]}')
            else:
                logger.debug(f'Skipped "{path}"')

        if queue:
            while True:
                try:
                    entry = heapq.heappop(queue)  # queue entry's indexes: 0 - priority, 1 - counter, 2 - task
                    yield entry[2]
                except IndexError:
                    break

    def run(self):
        do_initial_jobs()

        file_counter = 0
        for file, processors in self._get_tasks():
            logger.info(f'Processing "{file.path}"')
            for processor in processors:
                file = processor.process(file)
            file_counter += 1

        do_final_jobs()

        return file_counter
