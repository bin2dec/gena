import pytest
import os

from gena.files import FilePath


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


@pytest.fixture(name='file_path')
def _file_path(sample_file_path):
    return FilePath(sample_file_path.path)


class TestFilePath:
    def test_acceptance_many_paths(self, sample_file_path):
        file_path = FilePath(sample_file_path.directory, sample_file_path.name)
        assert file_path.path == sample_file_path.path

    def test_basename_property_getter(self, file_path, sample_file_path):
        assert file_path.basename == sample_file_path.basename

    def test_basename_property_setter(self, file_path, sample_file_path):
        file_path.basename = sample_file_path.basename = 'gateway-ridge'
        assert file_path.basename == sample_file_path.basename
        assert file_path.name == sample_file_path.name
        assert file_path.path == sample_file_path.path

    def test_basename_property_setter_with_separator(self, file_path):
        with pytest.raises(ValueError):
            file_path.basename = f'{os.sep}gateway-ridge'

    def test_directory_property_getter(self, file_path, sample_file_path):
        assert file_path.directory == sample_file_path.directory

    def test_directory_property_setter(self, file_path, sample_file_path):
        file_path.directory = sample_file_path.directory = 'data'
        assert file_path.directory == sample_file_path.directory
        assert file_path.path == sample_file_path.path

    def test_extension_property_getter(self, file_path, sample_file_path):
        assert file_path.extension == sample_file_path.extension

    @pytest.mark.parametrize('extension', ('html', '.html'))
    def test_extension_property_setter(self, extension, file_path, sample_file_path):
        file_path.extension = extension
        sample_file_path.extension = '.html'
        assert file_path.extension == sample_file_path.extension
        assert file_path.name == sample_file_path.name
        assert file_path.path == sample_file_path.path

    def test_name_property_getter(self, file_path, sample_file_path):
        assert file_path.name == sample_file_path.name

    def test_name_property_setter(self, file_path, sample_file_path):
        sample_file_path.basename = 'gateway-ridge'
        sample_file_path.extension = '.html'
        file_path.name = sample_file_path.name
        assert file_path.name == sample_file_path.name
        assert file_path.path == sample_file_path.path

    def test_path_object_copying(self, file_path):
        new_file_path = file_path.copy()
        assert file_path == new_file_path
        assert file_path is not new_file_path

    def test_path_object_equality(self, file_path, sample_file_path):
        new_file_path = FilePath(sample_file_path.path)
        assert file_path == new_file_path

    def test_path_property_getter(self, file_path, sample_file_path):
        assert file_path.path == sample_file_path.path

    def test_path_property_setter(self, file_path, sample_file_path):
        sample_file_path.directory = 'data'
        sample_file_path.basename = 'gateway-ridge'
        sample_file_path.extension = '.html'
        file_path.path = sample_file_path.path
        assert file_path.path == sample_file_path.path


class TestBinaryFile:
    def test_contents_property_getter(self, binary_file, sample_binary_contents):
        assert binary_file.contents == sample_binary_contents

    def test_contents_property_setter(self, binary_file):
        binary_file.contents = b'test'
        assert binary_file.contents == b'test'

    def test_contents_property_setter_with_bytes(self, binary_file):
        with pytest.raises(TypeError):
            binary_file.contents = 'test'

    def test_is_binary_method(self, binary_file):
        assert binary_file.is_binary()

    def test_is_text_method(self, binary_file):
        assert not binary_file.is_text()

    def test_saving_file_when_path_changed(self, binary_file, sample_binary_contents, tmpdir):
        tmpfile = tmpdir.join(binary_file.path.name)
        binary_file.path.path = tmpfile
        assert binary_file.save()
        assert tmpfile.read_binary() == sample_binary_contents
        assert not binary_file.save()  # the file isn't changed since the last saving

    def test_saving_file_when_path_and_contents_changed(self, binary_file, tmpdir):
        tmpfile = tmpdir.join(binary_file.path.name)
        binary_file.path.path = tmpfile
        binary_file.contents = b'test'
        assert binary_file.save()
        assert tmpfile.read_binary() == b'test'
        assert not binary_file.save()

    def test_saving_file_when_nothing_changed(self, binary_file):
        assert not binary_file.save()


class TestTextFile:
    def test_contents_property_getter(self, sample_text_contents, text_file):
        assert text_file.contents == sample_text_contents

    def test_contents_property_setter(self, text_file):
        text_file.contents = 'test'
        assert text_file.contents == 'test'

    def test_contents_property_setter_with_bytes(self, text_file):
        with pytest.raises(TypeError):
            text_file.contents = b'test'

    def test_is_binary_method(self, text_file):
        assert not text_file.is_binary()

    def test_is_text_method(self, text_file):
        assert text_file.is_text()

    def test_saving_file_when_path_changed(self, sample_text_contents, text_file, tmpdir):
        tmpfile = tmpdir.join(text_file.path.name)
        text_file.path.path = tmpfile
        assert text_file.save()
        assert tmpfile.read() == sample_text_contents
        assert not text_file.save()  # the file isn't changed since the last saving

    def test_saving_file_when_path_and_contents_changed(self, text_file, tmpdir):
        tmpfile = tmpdir.join(text_file.path.name)
        text_file.path.path = tmpfile
        text_file.contents = 'test'
        assert text_file.save()
        assert tmpfile.read() == 'test'
        assert not text_file.save()

    def test_saving_file_when_nothing_changed(self, text_file):
        assert not text_file.save()
