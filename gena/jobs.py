from __future__ import annotations

import jinja2
import os

from htmlmin import minify as html_minify
from shutil import rmtree
from typing import Iterable

from gena import utils
from gena.context import context
from gena.files import File
from gena.settings import settings


def do_jobs(jobs: Iterable):
    for job in jobs:
        obj = job['job']
        if not callable(obj):
            obj = utils.import_attr(obj)
        options = job.get('options', {})
        obj(**options)


def do_initial_jobs():
    do_jobs(settings.INITIAL_JOBS)


def do_final_jobs():
    do_jobs(settings.FINAL_JOBS)


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


def generate_file_from_template(filename: str = 'index.html', *, template: str = 'index.html',
                                minify: bool = False) -> None:
    j2_loader = jinja2.FileSystemLoader(searchpath=settings.TEMPLATE_DIRS)
    j2_environment = jinja2.Environment(loader=j2_loader, **settings.JINJA2_OPTIONS)
    j2_template = j2_environment.get_template(template)

    file = File(filename)
    file.path.directory = settings.DST_DIR
    file.contents = j2_template.render({**context, **settings})
    if minify:
        file.contents = html_minify(file.contents, **settings.HTML_MINIFIER_OPTIONS)
    file.save()
