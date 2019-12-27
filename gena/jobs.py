"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import logging
import os

from shutil import rmtree
from typing import Iterable

from gena import utils
from gena.exceptions import JobError
from gena.settings import settings
from gena.utils import map_as_kwargs


__all__ = (
    'clear_dst_dir',
    'run_final_jobs',
    'run_initial_jobs',
    'run_jobs',
)


logger = logging.getLogger(__name__)


def run_jobs(jobs: Iterable):
    """Run jobs from the given list.

    A job is a special callable object that can be called before or after the file processing.
    An example of a valid job list (can be declared in your settings):

    INITIAL_JOBS = (
        {'job': 'gena.jobs.clear_dst_dir'},
    )
    """

    debug = logger.isEnabledFor(logging.DEBUG)

    jobs_num = len(jobs)

    for i, job in enumerate(jobs, start=1):
        obj = job['job']
        if not callable(obj):
            obj = utils.import_attr(obj)
        options = job.get('options', {})
        if debug:
            logger.debug('Running the %s(%s) job (%s/%s)', obj.__name__, map_as_kwargs(options), i, jobs_num)
        try:
            obj(**options)
        except JobError as e:
            logger.critical('The %s job has been aborted! %s', obj.__name__, e.message)


def run_initial_jobs():
    """Initial jobs are called before the file processing."""
    logger.debug('Starting the initial jobs (%s total)...', len(settings.INITIAL_JOBS))
    run_jobs(settings.INITIAL_JOBS)


def run_final_jobs():
    """Final jobs are called after the file processing."""
    logger.debug('Starting the final jobs (%s total)...', len(settings.FINAL_JOBS))
    run_jobs(settings.FINAL_JOBS)


def clear_dst_dir() -> None:
    """Remove the contents of the destination directory.

    This job can be especially useful as an initial job. Just add these lines to your settings file:

    INITIAL_JOBS = (
        {'job': 'gena.jobs.clear_dst_dir'},
    )

    Now, before the file processing, your directory will be thoroughly cleaned up!
    """

    if not os.path.exists(settings.DST_DIR):
        return

    with os.scandir(settings.DST_DIR) as scandir:
        for file in scandir:
            if file.is_file():
                os.remove(file)
            else:
                rmtree(file)
