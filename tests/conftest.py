import pytest
import os

from dataclasses import dataclass

from gena.context import context as gena_context
from gena.files import File, FileType
from gena.settings import settings as gena_settings


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


@dataclass
class SampleArticlePath:
    directory: str = DATA_DIR
    basename: str = 'article'
    extension: str = '.md'

    def __fspath__(self):
        return self.path

    @property
    def name(self) -> str:
        return os.path.join(f'{self.basename}{self.extension}')

    @property
    def path(self) -> str:
        return os.path.join(self.directory, self.name)


@pytest.fixture
def sample_article_path():
    return SampleArticlePath()


@pytest.fixture(scope='session')
def sample_article_as_bytes():
    with open(SampleArticlePath(), 'rb') as file:
        return file.read()


@pytest.fixture(scope='session')
def sample_article_as_str():
    with open(SampleArticlePath(), 'rt') as file:
        return file.read()


@pytest.fixture
def article_binary_file(sample_article_path):
    return File(sample_article_path, file_type=FileType.BINARY)


@pytest.fixture
def article_text_file(sample_article_path):
    return File(sample_article_path, file_type=FileType.TEXT)


@pytest.fixture
def context():
    gena_context.clear()
    return gena_context


@pytest.fixture
def settings():
    gena_settings.clear()
    return gena_settings
