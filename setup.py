from setuptools import setup

setup(
    name='github_fork_explorer',
    version='0.0.1',
    packages=['forkexplorer', 'forkexplorer.tests'],
    url='https://github.com/raph92/forkexplorer',
    license='',
    author='raphael',
    author_email='rtnanje@gmail.com',
    description='Easily get the latest fork of a Github repo',
    entry_points={
        'console_scripts': ['forkexplorer=forkexplorer.cli:main'],
    },
)
