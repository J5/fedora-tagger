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


def get_requires(filename="requirements.txt"):
    with open(filename, 'r') as f:
        return f.readlines()

def get_tests_require(filename="test-requirements.txt"):
    with open(filename, 'r') as f:
        return f.readlines()

setup(
    name='fedoratagger',
    description='A web application for tagging and ranking packages',
    version='2.0.0a',
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
    '''
)
