import os
import subprocess
import sys

from contextlib import contextmanager
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

MECAB_KO_URL = 'https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.2.tar.gz'
MECAB_KO_DIC_URL = 'https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.0.3-20170922.tar.gz'


@contextmanager
def change_directory(directory):
    original = os.path.abspath(os.getcwd())

    os.chdir(directory)
    yield

    os.chdir(original)


def path_of(filename):
    for path, _, filenames in os.walk(os.getcwd()):
        if filename in filenames:
            return path

    raise ValueError('File {} not found'.format(filename))


def fancy_print(*args, color=None, bold=False, **kwargs):
    if bold:
        print('\033[1m', end='')

    if color:
        print('\033[{}m'.format(color), end='')

    print(*args, **kwargs)

    print('\033[0m', end='')  # reset


def install(url, *args):
    def download(url):
        components = urlparse(url)
        filename = os.path.basename(components.path)

        subprocess.check_call([
            'wget',
            '--progress=dot:binary',
            '--output-document={}'.format(filename),
            url,
        ])
        subprocess.check_call(['tar', '-xzf', filename])

    def configure(*args):
        with change_directory(path_of('configure')):
            subprocess.check_call(['./configure', *args])

    def make():
        with change_directory(path_of('Makefile')):
            subprocess.check_call(['make'])
            subprocess.check_call(['make', 'install'])

    with TemporaryDirectory() as directory:
        with change_directory(directory):
            download(url)
            configure(*args)
            make()


if __name__ == '__main__':
    fancy_print('Installing mecab-ko...', color=32, bold=True)
    install(MECAB_KO_URL, '--prefix={}'.format(sys.prefix),
                          '--enable-utf8-only')

    fancy_print('Installing mecab-ko-dic...', color=32, bold=True)
    mecab_config_path = os.path.join(sys.prefix, 'bin', 'mecab-config')
    install(MECAB_KO_DIC_URL, '--prefix={}'.format(sys.prefix),
                              '--with-charset=utf8',
                              '--with-mecab-config={}'.format(mecab_config_path))
