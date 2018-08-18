import pytest
import os

from gena.files import FilePath


@pytest.fixture
def article_file_path(sample_article_path):
    return FilePath(sample_article_path)


class TestFilePath:
    def test_acceptance_many_paths(self, sample_article_path):
        file_path = FilePath(sample_article_path.directory, sample_article_path.name)
        assert file_path.path == sample_article_path.path

    def test_basename_property_getter(self, article_file_path, sample_article_path):
        assert article_file_path.basename == sample_article_path.basename

    def test_basename_property_setter(self, article_file_path, sample_article_path):
        article_file_path.basename = sample_article_path.basename = 'gateway-ridge'
        assert article_file_path.basename == sample_article_path.basename
        assert article_file_path.name == sample_article_path.name
        assert article_file_path.path == sample_article_path.path

    def test_basename_property_setter_with_separator(self, article_file_path):
        with pytest.raises(ValueError):
            article_file_path.basename = f'{os.sep}gateway-ridge'

    def test_directory_property_getter(self, article_file_path, sample_article_path):
        assert article_file_path.directory == sample_article_path.directory

    def test_directory_property_setter(self, article_file_path, sample_article_path):
        article_file_path.directory = sample_article_path.directory = 'output'
        assert article_file_path.directory == sample_article_path.directory
        assert article_file_path.path == sample_article_path.path

    def test_extension_property_getter(self, article_file_path, sample_article_path):
        assert article_file_path.extension == sample_article_path.extension

    @pytest.mark.parametrize('extension', ('html', '.html'))
    def test_extension_property_setter(self, article_file_path, extension, sample_article_path):
        article_file_path.extension = extension
        sample_article_path.extension = '.html'
        assert article_file_path.extension == sample_article_path.extension
        assert article_file_path.name == sample_article_path.name
        assert article_file_path.path == sample_article_path.path

    def test_name_property_getter(self, article_file_path, sample_article_path):
        assert article_file_path.name == sample_article_path.name

    def test_name_property_setter(self, article_file_path, sample_article_path):
        sample_article_path.basename = 'gateway-ridge'
        sample_article_path.extension = '.html'
        article_file_path.name = sample_article_path.name
        assert article_file_path.name == sample_article_path.name
        assert article_file_path.path == sample_article_path.path

    def test_path_object_copying(self, article_file_path):
        new_file_path = article_file_path.copy()
        assert article_file_path == new_file_path
        assert article_file_path is not new_file_path

    def test_path_object_equality(self, article_file_path, sample_article_path):
        new_file_path = FilePath(sample_article_path.path)
        assert article_file_path == new_file_path

    def test_path_property_getter(self, article_file_path, sample_article_path):
        assert article_file_path.path == sample_article_path.path

    def test_path_property_setter(self, article_file_path, sample_article_path):
        sample_article_path.directory = 'output'
        sample_article_path.basename = 'gateway-ridge'
        sample_article_path.extension = '.html'
        article_file_path.path = sample_article_path.path
        assert article_file_path.path == sample_article_path.path


class TestBinaryFile:
    def test_contents_property_getter(self, article_binary_file, sample_article_as_bytes):
        assert article_binary_file.contents == sample_article_as_bytes

    def test_contents_property_setter(self, article_binary_file):
        article_binary_file.contents = b'test'
        assert article_binary_file.contents == b'test'

    def test_contents_property_setter_with_bytes(self, article_binary_file):
        with pytest.raises(TypeError):
            article_binary_file.contents = 'test'

    def test_is_binary_method(self, article_binary_file):
        assert article_binary_file.is_binary()

    def test_is_text_method(self, article_binary_file):
        assert not article_binary_file.is_text()

    def test_saving_file_when_path_changed(self, article_binary_file, sample_article_as_bytes, tmpdir):
        tmpfile = tmpdir.join(article_binary_file.path.name)
        article_binary_file.path.path = tmpfile
        assert article_binary_file.save()
        assert tmpfile.read_binary() == sample_article_as_bytes
        assert not article_binary_file.save()  # the file isn't changed since the last saving

    def test_saving_file_when_contents_changed(self, article_binary_file):
        article_binary_file.contents = b'test'
        assert not article_binary_file.save()

    def test_saving_file_when_path_and_contents_changed(self, article_binary_file, tmpdir):
        tmpfile = tmpdir.join(article_binary_file.path.name)
        article_binary_file.path.path = tmpfile
        article_binary_file.contents = b'test'
        assert article_binary_file.save()
        assert tmpfile.read_binary() == b'test'
        assert not article_binary_file.save()

    def test_saving_file_when_nothing_changed(self, article_binary_file):
        assert not article_binary_file.save()


class TestTextFile:
    def test_contents_property_getter(self, article_text_file, sample_article_as_str):
        assert article_text_file.contents == sample_article_as_str

    def test_contents_property_setter(self, article_text_file):
        article_text_file.contents = 'test'
        assert article_text_file.contents == 'test'

    def test_contents_property_setter_with_bytes(self, article_text_file):
        with pytest.raises(TypeError):
            article_text_file.contents = b'test'

    def test_is_binary_method(self, article_text_file):
        assert not article_text_file.is_binary()

    def test_is_text_method(self, article_text_file):
        assert article_text_file.is_text()

    def test_saving_file_when_path_changed(self, article_text_file, sample_article_as_str, tmpdir):
        tmpfile = tmpdir.join(article_text_file.path.name)
        article_text_file.path.path = tmpfile
        assert article_text_file.save()
        assert tmpfile.read() == sample_article_as_str
        assert not article_text_file.save()  # the file isn't changed since the last saving

    def test_saving_file_when_contents_changed(self, article_text_file):
        article_text_file.contents = 'test'
        assert not article_text_file.save()

    def test_saving_file_when_path_and_contents_changed(self, article_text_file, tmpdir):
        tmpfile = tmpdir.join(article_text_file.path.name)
        article_text_file.path.path = tmpfile
        article_text_file.contents = 'test'
        assert article_text_file.save()
        assert tmpfile.read() == 'test'
        assert not article_text_file.save()

    def test_saving_file_when_nothing_changed(self, article_text_file):
        assert not article_text_file.save()
