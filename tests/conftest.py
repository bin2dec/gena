import pytest
import os

from dataclasses import dataclass

from gena.files import File, FileType


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


@dataclass
class SampleFilePath:
    directory: str = DATA_DIR
    basename: str = 'article'
    extension: str = '.md'

    @property
    def name(self) -> str:
        return os.path.join(f'{self.basename}{self.extension}')

    @property
    def path(self) -> str:
        return os.path.join(self.directory, self.name)


@pytest.fixture(name='sample_file_path')
def _sample_file_path():
    return SampleFilePath()


@pytest.fixture(name='sample_binary_contents', scope='session')
def _sample_binary_contents():
    sample_file_path = SampleFilePath()
    with open(sample_file_path.path, 'rb') as file:
        return file.read()


@pytest.fixture(name='sample_text_contents', scope='session')
def _sample_text_contents():
    sample_file_path = SampleFilePath()
    with open(sample_file_path.path, 'rt') as file:
        return file.read()


@pytest.fixture(name='binary_file')
def _binary_file(sample_file_path):
    return File(sample_file_path.path, file_type=FileType.BINARY)


@pytest.fixture(name='text_file')
def _text_file(sample_file_path):
    return File(sample_file_path.path, file_type=FileType.TEXT)
