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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA
#
# Refer to the README.rst and LICENSE files for full details of the license
# -*- coding: utf-8 -*-

'''
taggerapi tests.
'''

__requires__ = ['SQLAlchemy >= 0.7']
import pkg_resources

import unittest
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import taggerapi.taggerlib
from taggerapi.taggerlib import model

DB_URL = 'sqlite:///:memory:'


class Modeltests(unittest.TestCase):
    """ Model tests. """

    def __init__(self, method_name='runTest'):
        """ Constructor. """
        unittest.TestCase.__init__(self, method_name)
        self.session = None

    # pylint: disable=C0103
    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        self.session = model.create_tables(DB_URL)

    # pylint: disable=C0103
    def tearDown(self):
        """ Remove the test.db database if there is one. """
        if os.path.exists(DB_URL):
            os.unlink(DB_URL)

        self.session.rollback()


def create_package(session):
    """ Create some basic Package for testing. """
    package = model.Package(
                                  name = 'guake',
                                  summary = 'drop-down terminal for gnome',
                                  )
    session.add(package)

    package = model.Package(
                                  name = 'geany',
                                  summary = 'IDE for Gnome',
                                  )
    session.add(package)

    package = model.Package(
                                  name = 'gitg',
                                  summary = 'GTK+ graphical interface for'
                                  ' the git revision control system',
                                  )
    session.add(package)

    session.commit()


def create_tag(session):
    """ Add Tags on packages. """

    taggerapi.taggerlib.add_tag(session, 'guake', 'gnome', 'pingou')
    taggerapi.taggerlib.add_tag(session, 'guake', 'terminal', 'pingou')
    taggerapi.taggerlib.add_tag(session, 'geany', 'ide', 'pingou')
    taggerapi.taggerlib.add_tag(session, 'geany', 'gnome', 'pingou')

    session.commit()


def create_rating(session):
    """ Add Vote on tags of packages. """

    taggerapi.taggerlib.add_rating(session, 'guake', 100, 'pingou')
    taggerapi.taggerlib.add_rating(session, 'guake', 50, 'toshio')
    taggerapi.taggerlib.add_rating(session, 'geany', 100, 'ralph')

    session.commit()


def create_vote(session):
    """ Add Vote on tags of packages. """

    taggerapi.taggerlib.add_vote(session, 'guake', 'gnome', True, 'toshio')
    taggerapi.taggerlib.add_vote(session, 'guake', 'terminal', False, 'toshio')
    taggerapi.taggerlib.add_tag(session, 'geany', 'ide', True, 'kevin')

    session.commit()


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Modeltests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
