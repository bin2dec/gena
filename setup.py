import os.path
import re

from setuptools import find_packages, setup


REQUIRES = [
    'htmlmin >= 0.1.12',
    'jinja2 >= 2.10',
    'markdown >= 2.6.11',
    'python-dateutil >= 2.7.3',
    'python-slugify >= 1.2.5',
]

BASE_DIR = os.path.dirname(__file__)


def get_file_contents(*paths):
    path = os.path.join(BASE_DIR, *paths)
    with open(path) as file:
        return file.read()


def get_long_description():
    return get_file_contents('README.md')


def get_version():
    file_contents = get_file_contents('gena', '__init__.py')
    version = re.match(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', file_contents, re.M)
    if version:
        return version.group(1)
    raise RuntimeError('Unable to find version string.')


setup(
    name='GenA',
    version=get_version(),
    description='A universal static site generator.',
    long_description=get_long_description(),
    author='Dmitriy Pakhomov',
    author_email='d_pakhomoff@gmail.com',
    license='AGPLv3',
    url='https://gitlab.com/dec0der/gena',
    python_requires='>=3.7',
    install_requires=REQUIRES,
    tests_require=['pytest'],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'gena = gena.__main__:main',
        ],
    },
)