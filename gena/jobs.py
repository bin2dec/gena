from __future__ import annotations

import jinja2

from htmlmin import minify as html_minify
from typing import Iterable

from gena import utils
from gena.context import context
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


def generate_file_from_template(filename: str = 'index.html', *, template: str = 'index.html',
                                minify: bool = False) -> None:
    j2_loader = jinja2.FileSystemLoader(searchpath=settings.TEMPLATE_DIRS)
    j2_environment = jinja2.Environment(loader=j2_loader, **settings.JINJA2_OPTIONS)
    j2_template = j2_environment.get_template(template)

    file_class = utils.import_attr(settings.FILE)
    file = file_class(filename)
    file.path.directory = settings.DST_DIR
    file.contents = j2_template.render({**context, **settings})
    if minify:
        file.contents = html_minify(file.contents, **settings.HTML_MINIFIER_OPTIONS)
    file.save()
