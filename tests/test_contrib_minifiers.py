import os.path

from gena.contrib.minifiers import HTMLMinifierProcessor
from gena.files import File


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')


class TestHTMLMinifierProcessor:
    def test_processing(self):
        with open(os.path.join(OUTPUT_DIR, 'gateway-ridge.min.html')) as file:
            sample_contents = file.read()
        input_file = File(OUTPUT_DIR, 'gateway-ridge.html')
        processor = HTMLMinifierProcessor()
        output_file = processor.process(input_file)
        assert output_file.contents == sample_contents
