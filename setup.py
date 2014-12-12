#!/usr/bin/env python
"""
Setup script
"""

from setuptools import setup

try:
    import logging
    import multiprocessing
except ImportError:
    pass


def strip_comments(lines):
    for line in lines:
        line = line.strip()

        if line.startswith('#') or not line:
            continue

        if '#' not in line:
            yield line
        else:
            yield line[:line.index('#')]


def get_requires(filename="requirements.txt"):
    with open(filename, 'r') as f:
        return list(strip_comments(f.readlines()))


def get_tests_require(filename="test-requirements.txt"):
    with open(filename, 'r') as f:
        return list(strip_comments(f.readlines()))

setup(
    name='fedora-tagger',
    description='A web application for tagging and ranking packages',
    version='2.2.1',
    author='Pierre-Yves Chibon and Ralph Bean',
    author_email='pingou@pingoured.fr, ralph@fedoraproject.org',
    license='GPLv2+',
    url='https://github.com/fedora-infra/fedora-tagger/',
    packages=['fedoratagger'],
    include_package_data=True,
    install_requires=get_requires(),
    test_suite='nose.collector',
    tests_require=get_tests_require(),
    entry_points='''
    [tw2.widgets]
    widgets = fedoratagger.frontend.widgets

    [console_scripts]
    fedoratagger-update-db = fedoratagger.lib.update:main
    fedoratagger-remove-pkgs = fedoratagger.lib.retired:main
    fedoratagger-merge-tag = fedoratagger.lib.merge_tags:main
    '''
)
