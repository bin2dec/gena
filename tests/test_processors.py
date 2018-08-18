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
    def test_processing_when_name_is_string(self, article_text_file, sample_article_path):
        sample_article_path.extension = '.html'
        processor = FileNameProcessor(name=sample_article_path.name)
        output_file = processor.process(article_text_file)
        assert output_file.path.name == sample_article_path.name
        assert output_file.path.path == sample_article_path.path

    def test_processing_when_name_is_callable(self, article_text_file, sample_article_path):
        sample_article_path.extension = '.html'
        processor = FileNameProcessor(name=lambda file: f'{file.path.basename}{sample_article_path.extension}')
        output_file = processor.process(article_text_file)
        assert output_file.path.name == sample_article_path.name
        assert output_file.path.path == sample_article_path.path
