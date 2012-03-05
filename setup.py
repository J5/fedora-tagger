# This file is a part of Fedora Tagger
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Refer to the README.rst and LICENSE files for full details of the license
# -*- coding: utf-8 -*-
#quckstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       True
#
#

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=['WebTest >= 1.2.3',
               'nose',
               'coverage',
               'wsgiref',
               'repoze.who-testutil >= 1.0.1',
               ]

install_requires=[
    "Pylons<=1.0",      # This is madness
    "WebOb<=1.0.8",     # This is also madness
    "repoze.who<=1.99", # Madness, still
    "TurboGears2",
    "Mako",
    "zope.sqlalchemy >= 0.4",
    "repoze.tm2",
    "sqlalchemy",
    "repoze.what >= 1.0.8",
    "repoze.who-friendlyform >= 1.0.4",
    "repoze.what-pylons >= 1.0",
    "repoze.what.plugins.sql",
    "bunch",
    "kitchen",
    "python-fedora",
    "pycurl",
    "tw2.core",
    "tw2.jqplugins.gritter",
    "tw2.jqplugins.ui>=2.0b26",
    "docutils",
    "fedmsg>=0.0.1a4",
    ]

if sys.version_info[:2] == (2,4):
    testpkgs.extend(['hashlib', 'pysqlite'])
    install_requires.extend(['hashlib', 'pysqlite'])

setup(
    name='fedora-tagger',
    version='0.1.1',
    description='',
    author='Ralph Bean',
    author_email='ralph.bean@gmail.com',
    url='http://github.com/ralphbean/fedora-tagger',
    license="GPLv2+",
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'fedoratagger': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 #'public/*/*'
                                 ]},
    message_extractors={'fedoratagger': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = fedoratagger.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [tw2.widgets]
    widgets = fedoratagger.widgets
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
        ],
    zip_safe=False
)
