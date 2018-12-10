import fnmatch
import heapq
import itertools
import logging
import os
import re

from gena import utils
from gena.exceptions import StopProcessing
from gena.jobs import do_final_jobs, do_initial_jobs
from gena.settings import settings


__all__ = (
    'FileRunner',
)


logger = logging.getLogger(__name__)


class FileRunner:
    def __init__(self):
        rules = settings.RULES or settings.get('PROCESSING_RULES', ())

        if not rules:
            raise ValueError('no rules are found to process')

        default_file_factory = utils.import_attr(settings.DEFAULT_FILE_FACTORY)

        self._rules = []
        for rule in rules:
            if 'retest' in rule:
                new_test = os.path.normcase(rule['retest'])
                logger.debug('Got a rule for "%s"', rule['retest'])
            else:
                new_test = os.path.normcase(rule['test'])
                new_test = fnmatch.translate(new_test)
                logger.debug('Got a rule for "%s"', rule['test'])
            new_test = re.compile(new_test).search

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
            if rule['test'](os.path.normcase(path)):
                return rule

    def _get_tasks(self):
        if not self._rules:
            return

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
        tasks = self._get_tasks()
        if not tasks:
            return []

        do_initial_jobs()

        files = []
        for file, processors in tasks:
            logger.info('Processing "%s"', file.path)
            for processor in processors:
                try:
                    file = processor(file)
                except StopProcessing as e:
                    logger.debug('Stop processing "%s". %s', e.file, e.message)
                    break
            files.append(file)

        do_final_jobs()

        return files
