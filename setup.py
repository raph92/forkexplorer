import re
from os import path
from setuptools import setup
from io import open as io_open

here = path.abspath(path.dirname(__file__))

with open("requirements.txt") as f:
    dependencies = f.read().splitlines()


def readall(*args):
    with io_open(path.join(here, *args), encoding="utf-8") as fp:
        return fp.read()


metadata = dict(
    re.findall(r"""__([a-z]+)__ = "([^"]+)""", readall("forkexplorer", "__init__.py"))
)
setup(
    name='forkexplorer',
    version=metadata["version"],
    packages=['forkexplorer', 'forkexplorer.tests'],
    url='https://github.com/raph92/forkexplorer',
    license="GPLv3",
    author='Raphael N',
    author_email='rtnanje@gmail.com',
    maintainer="Raphael N",
    description='Easily get the latest fork of a Github repo',
    entry_points={
        'console_scripts': ['forkexplorer=forkexplorer.cli:main'],
    },
    install_requires=dependencies,
    platforms=["linux", "linux2"],
)
