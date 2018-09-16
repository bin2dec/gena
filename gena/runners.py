import fnmatch
import heapq
import itertools
import logging
import os
import re

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

    debug = logger.isEnabledFor(logging.DEBUG)

    for job in jobs:
        obj = job['job']
        if not callable(obj):
            obj = utils.import_attr(obj)
        options = job.get('options', {})
        if debug:
            logger.debug('Doing the %s(%s) job', obj.__name__, map_as_kwargs(options))
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
        rules = settings.RULES or settings.get('PROCESSING_RULES', ())

        if rules:
            default_file_factory = utils.import_attr(settings.DEFAULT_FILE_FACTORY)
        else:
            logger.warning('No rules are found to process')

        self._rules = []
        for rule in rules:
            new_test = os.path.normpath(rule['test'])
            new_test = fnmatch.translate(new_test)
            new_test = re.compile(new_test).match

            new_processors = []
            for processor in rule['processors']:
                new_processor = utils.import_attr(processor['processor'])
                new_processor = new_processor(**processor.get('options', {}))
                new_processors.append(new_processor.process)

            if 'file_factory' in rule:
                new_file_factory = utils.import_attr(rule['file_factory'])
            else:
                new_file_factory = default_file_factory

            new_rule = {
                'test': new_test,
                'processors': new_processors,
                'file_factory': new_file_factory,
                'priority': rule.get('priority', settings.DEFAULT_PRIORITY),
            }
            self._rules.append(new_rule)

    def _get_paths(self):
        for root, _, files in os.walk(settings.SRC_DIR):
            for file in files:
                yield os.path.join(root, file)

    def _get_rule(self, path):
        for rule in self._rules:
            if rule['test'](os.path.normpath(path)):
                return rule

    def _get_tasks(self):
        counter = itertools.count()  # the counter is needed in situations when priorities are equal
        queue = []

        for path in self._get_paths():
            rule = self._get_rule(path)
            if rule:
                file = rule['file_factory'](path)
                task = (file, rule['processors'])
                entry = (rule['priority'], next(counter), task)
                heapq.heappush(queue, entry)
                logger.debug('Created a task for "%s" with priority=%s', file.path, rule['priority'])
            else:
                logger.debug('Skipped "%s"', path)

        if queue:
            while True:
                try:
                    entry = heapq.heappop(queue)  # queue entry's indexes: 0 - priority, 1 - counter, 2 - task
                    yield entry[2]
                except IndexError:
                    break

    def run(self):
        if not self._rules:
            return 0

        do_initial_jobs()

        file_counter = 0
        for file, processors in self._get_tasks():
            logger.info('Processing "%s"', file.path)
            for processor in processors:
                file = processor(file)
            file_counter += 1

        do_final_jobs()

        return file_counter
