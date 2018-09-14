"""The module contains a bunch of initial and final jobs."""

from __future__ import annotations

import os

from shutil import rmtree

from gena.settings import settings


def clear_dst_dir() -> None:
    """Remove the contents of the destination directory.

    This job can be especially useful as an initial job. Just add these lines to your settings file:

    INITIAL_JOBS = (
        {'job': 'gena.jobs.clear_dst_dir'},
    )

    Now, before the file processing, your directory will be thoroughly cleaned up!
    """

    with os.scandir(settings.DST_DIR) as scandir:
        for file in scandir:
            if file.is_file():
                os.remove(file)
            else:
                rmtree(file)
