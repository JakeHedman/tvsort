from setuptools import setup

setup(
    version='0.1',
    name = "tvsort",
    packages = ['tvsort'],
    description='Sort TV episodes',
    author='Jakob Hedman',
    author_email='jakob@hedman.email',
    maintainer='Jakob Hedman',
    maintainer_email='jakob@hedman.email',
    license='GNU GPLv3',
    url='https://github.com/spillevink/tvsort',
    package_dir = {'tvsort':'tvsort'},
    entry_points = {
        'console_scripts': [
            'tvsort = tvsort.tvsort:main.command',
        ],
    },
    install_requires = [
        'opster',
        'configobj',
    ],
    long_description = open('README.rst').read(),
)
