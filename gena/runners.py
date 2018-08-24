import os

from fnmatch import fnmatch

from gena import utils
from gena.jobs import do_final_jobs, do_initial_jobs
from gena.settings import settings


__all__ = (
    'FileRunner',
)


class FileRunner(object):
    def __init__(self, src):
        self._src = src

        default_file_factory = utils.import_attr(settings.DEFAULT_FILE_FACTORY)
        default_file_factory = default_file_factory()

        self._processing_rules = []
        for rule in settings.PROCESSING_RULES:
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
            }
            self._processing_rules.append(new_rule)

    def _get_paths(self):
        for dirpath, _, filenames in os.walk(self._src):
            for filename in filenames:
                yield (dirpath, filename)

    def _get_rule(self, test):
        for rule in self._processing_rules:
            if fnmatch(test, rule['test']):
                return rule

    def run(self):
        do_initial_jobs()

        for dirpath, filename in self._get_paths():
            rule = self._get_rule(filename)
            if rule:
                file = rule['file_factory'](dirpath, filename)
                for processor in rule['processors']:
                    file = processor.process(file)

        do_final_jobs()
