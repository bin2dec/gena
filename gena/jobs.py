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
    'do_final_jobs',
    'do_initial_jobs',
    'do_jobs',
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
        try:
            obj(**options)
        except JobError as e:
            logger.critical('The %s job has been aborted! %s', obj.__name__, e.message)


def do_initial_jobs():
    """Initial jobs are called before the file processing."""
    logger.debug('Doing the initial jobs')
    do_jobs(settings.INITIAL_JOBS)


def do_final_jobs():
    """Final jobs are called after the file processing."""
    logger.debug('Doing the final jobs')
    do_jobs(settings.FINAL_JOBS)


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
