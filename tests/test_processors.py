import os.path
import sys

from gzip import compress
from string import capwords

from gena.files import File, FileType
from gena.processors import *


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')
UTILS_DIR = os.path.join(BASE_DIR, 'utils')


class TestBundleProcessor:
    def test_binary_file_processing(self, context):
        file1 = File('file1', type=FileType.BINARY)
        file1.contents = b'test1'
        file2 = File('file2', type=FileType.BINARY)
        file2.contents = b'test2'
        processor = BundleProcessor(name='test')
        processor.process(file1)
        processor.process(file2)
        assert context.bundles['test'] == b'test1test2'

    def test_text_file_processing(self, context):
        file1 = File('file1')
        file1.contents = 'test1'
        file2 = File('file2')
        file2.contents = 'test2'
        processor = BundleProcessor(name='test')
        processor.process(file1)
        processor.process(file2)
        assert context.bundles['test'] == 'test1test2'


class TestExternalProcessor:
    def test_binary_file_processing(self, article_binary_file):
        gzipped_contents = compress(article_binary_file.contents)
        util = os.path.join(UTILS_DIR, 'gzippy')
        processor = ExternalProcessor(command=[sys.executable, util])
        output_file = processor.process(article_binary_file)
        assert output_file.contents == gzipped_contents

    def test_text_file_processing(self, article_text_file):
        uppercased_contents = article_text_file.contents.upper()
        util = os.path.join(UTILS_DIR, 'uppercaser')
        processor = ExternalProcessor(command=[sys.executable, util])
        output_file = processor.process(article_text_file)
        assert output_file.contents == uppercased_contents


class TestFileMetaProcessor:
    def test_processing_with_defaults(self, article_text_file):
        article_text_file.meta['title'] = ['gateway ridge']
        processor = FileMetaProcessor(key='title', callback=capwords)
        output_file = processor.process(article_text_file)
        assert str(output_file.meta.title) == 'Gateway Ridge'

    def test_processing_when_callback_with_args(self, article_text_file):
        article_text_file.meta['title'] = ['gateway ridge']
        processor = FileMetaProcessor(key='title', callback=capwords, callback_args=' ')
        output_file = processor.process(article_text_file)
        assert str(output_file.meta.title) == 'Gateway Ridge'

    def test_processing_when_callback_with_kwargs(self, article_text_file):
        article_text_file.meta['title'] = ['gateway ridge']
        processor = FileMetaProcessor(key='title', callback=capwords, callback_kwargs={'sep': ' '})
        output_file = processor.process(article_text_file)
        assert str(output_file.meta.title) == 'Gateway Ridge'

    def test_processing_when_default_value_is_iterable(self, article_text_file):
        processor = FileMetaProcessor(key='title', callback=capwords, default=['gateway ridge'])
        output_file = processor.process(article_text_file)
        assert str(output_file.meta.title) == 'Gateway Ridge'

    def test_processing_when_default_value_is_callable(self, article_text_file):
        article_text_file.meta['heading'] = ['gateway ridge']
        processor = FileMetaProcessor(key='title', callback=capwords, default=lambda file: file.meta.heading)
        output_file = processor.process(article_text_file)
        assert str(output_file.meta.title) == 'Gateway Ridge'

    def test_processing_several_values(self, article_text_file):
        article_text_file.meta['title'] = ['gateway', 'ridge']
        processor = FileMetaProcessor(key='title', callback=capwords)
        output_file = processor.process(article_text_file)
        assert output_file.meta.title == ['Gateway', 'Ridge']

    def test_existing_data_skipping(self, article_text_file):
        article_text_file.meta['title'] = ['gateway ridge']
        processor = FileMetaProcessor(key='title', callback=capwords, skip_if_exists=True)
        output_file = processor.process(article_text_file)
        assert str(output_file.meta.title) == 'gateway ridge'


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


class TestGroupProcessor:
    def test_processing(self, article_text_file, context):
        processor = GroupProcessor(name='articles')
        output_file = processor.process(article_text_file)
        assert context.groups['articles'] == [output_file]


class TestHTMLMinifierProcessor:
    def test_processing(self):
        with open(os.path.join(OUTPUT_DIR, 'gateway-ridge.min.html')) as file:
            sample_contents = file.read()
        input_file = File(OUTPUT_DIR, 'gateway-ridge.html')
        processor = HTMLMinifierProcessor()
        output_file = processor.process(input_file)
        assert output_file.contents == sample_contents


class TestJinja2Processor:
    def test_processing(self, settings):
        with open(os.path.join(OUTPUT_DIR, 'gateway-ridge.html')) as file:
            sample_contents = file.read()
        input_file = File(OUTPUT_DIR, 'article.html')
        input_file.meta['title'] = ['Gateway Ridge']
        settings.TEMPLATE_DIRS = TEMPLATES_DIR
        processor = Jinja2Processor(template='article.html')
        output_file = processor.process(input_file)
        assert output_file.contents == sample_contents


class TestMarkdownProcessor:
    def test_processing(self, article_text_file):
        with open(os.path.join(OUTPUT_DIR, 'article.html')) as file:
            sample_contents = file.read()
        processor = MarkdownProcessor()
        output_file = processor.process(article_text_file)
        assert output_file.contents == sample_contents
        assert output_file.meta.title == ['Gateway Ridge']
        assert output_file.meta.date == ['20:29, 10 November 2010']
        assert output_file.meta.source == ['Wikipedia']
        assert output_file.meta.license == ['Creative Commons Attribution CC-BY-SA 4.0']
        assert output_file.meta.link == ['https://en.wikipedia.org/wiki/Gateway_Ridge']


class TestSavingProcessor:
    def test_processing_with_directory_renaming(self, article_text_file, sample_article_as_str, settings, tmpdir):
        tmpfile = tmpdir.join(article_text_file.path.name)
        settings.DST_DIR = tmpfile.dirpath()
        processor = SavingProcessor(rename_directory=True)
        processor.process(article_text_file)
        assert tmpfile.read() == sample_article_as_str

    def test_processing_without_directory_renaming(self, article_text_file, sample_article_as_str, tmpdir):
        tmpfile = tmpdir.join(article_text_file.path.name)
        article_text_file.path.path = tmpfile
        processor = SavingProcessor(rename_directory=False)
        processor.process(article_text_file)
        assert tmpfile.read() == sample_article_as_str


class TestTypeProcessor:
    def test_processing_binary_to_text(self, article_binary_file):
        processor = TypeProcessor(type=FileType.TEXT)
        output_file = processor.process(article_binary_file)
        assert output_file.type == FileType.TEXT

    def test_processing_text_to_binary(self, article_text_file):
        processor = TypeProcessor(type=FileType.BINARY)
        output_file = processor.process(article_text_file)
        assert output_file.type == FileType.BINARY

