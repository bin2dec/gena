import pytest
import os

from gena.processors import FileNameProcessor
from gena.settings import Settings


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


@pytest.fixture(name='settings', scope='module')
def _settings():
    settings = Settings()
    settings.load_from_module(os.path.join(BASE_DIR, 'settings.py'))
    return settings


class TestFileNameProcessor:
    def test_processing_when_name_is_string(self, sample_file_path, settings, text_file):
        sample_file_path.extension = '.html'
        processor = FileNameProcessor(settings=settings, name=sample_file_path.name)
        text_file = processor.process(text_file)
        assert text_file.path.name == sample_file_path.name
        assert text_file.path.path == sample_file_path.path

    def test_processing_when_name_is_callable(self, sample_file_path, settings, text_file):
        sample_file_path.extension = '.html'
        processor = FileNameProcessor(settings=settings,
                                      name=lambda file: f'{file.path.basename}{sample_file_path.extension}')
        text_file = processor.process(text_file)
        assert text_file.path.name == sample_file_path.name
        assert text_file.path.path == sample_file_path.path
