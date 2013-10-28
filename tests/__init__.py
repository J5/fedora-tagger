# -*- coding: utf-8 -*-
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

'''
fedoratagger tests.
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

import fedoratagger.lib
from fedoratagger.lib import model


DB_URL = 'sqlite:///:memory:'
#import requests
#DB_URL = requests.get('http://api.postgression.com').text

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

    def tearDown(self):
        self.session.close()
        # drop tables if we can
        try:
            engine = create_engine(DB_URL)
            model.DeclarativeBase.metadata.drop_all(engine)
        except Exception as e:
            print "Failed dropping tables %r" % e

        if os.path.exists(DB_URL):
            os.unlink(DB_URL)

        self.session.rollback()


class FakeUser(object):
    """ Fake user used for the tests. """
    id = 0
    username = 'fake_username'
    email = 'fake_usename@example.org'
    score = 0


def create_user(session):
    """ Create some users for testing. """
    user = model.FASUser(
                                  username = 'pingou',
                                  email = 'pingou@fp.o',
                                  )
    session.add(user)

    user = model.FASUser(
                                  username = 'toshio',
                                  email = 'toshio@fp.o',
                                  )
    session.add(user)

    user = model.FASUser(
                                  username = 'kevin',
                                  email = 'kevin@fp.o',
                                  )
    session.add(user)

    user = model.FASUser(
                                  username = 'skvidal',
                                  email = 'skvidal@fp.o',
                                  )
    session.add(user)

    user = model.FASUser(
                                  username = 'ralph',
                                  email = 'ralph@fp.o',
                                  )
    session.add(user)

    session.commit()


def create_package(session):
    """ Create some basic Package for testing. """
    package = model.Package(
                                  name = 'guake',
                                  summary = u'drop-down terminal for gnóme',
                                  )
    session.add(package)

    package = model.Package(
                                  name = 'geany',
                                  summary = u'IDE for gnóme',
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

    create_user(session)
    user_pingou = model.FASUser.by_name(session, 'pingou')
    user_toshio = model.FASUser.by_name(session, 'toshio')
    user_kevin = model.FASUser.by_name(session, 'kevin')
    user_skvidal = model.FASUser.by_name(session, 'skvidal')

    fedoratagger.lib.add_tag(session, 'guake', u'gnóme', user_pingou)
    fedoratagger.lib.add_tag(session, 'guake', 'terminal', user_pingou)
    fedoratagger.lib.add_tag(session, 'geany', 'ide', user_pingou)
    fedoratagger.lib.add_tag(session, 'geany', u'gnóme', user_pingou)

    fedoratagger.lib.add_tag(session, 'guake', u'gnóme', user_toshio)
    fedoratagger.lib.add_tag(session, 'guake', 'terminal', user_kevin)
    fedoratagger.lib.add_tag(session, 'geany', 'ide', user_skvidal)
    fedoratagger.lib.add_tag(session, 'geany', u'gnóme', user_toshio)

    session.commit()


def create_rating(session):
    """ Add Rating on packages. """

    create_user(session)
    user_pingou = model.FASUser.by_name(session, 'pingou')
    user_toshio = model.FASUser.by_name(session, 'toshio')
    user_ralph = model.FASUser.by_name(session, 'ralph')

    fedoratagger.lib.add_rating(session, 'guake', 100, user_pingou)
    fedoratagger.lib.add_rating(session, 'guake', 50, user_toshio)
    fedoratagger.lib.add_rating(session, 'geany', 100, user_ralph)

    session.commit()


def create_vote(session):
    """ Add Vote on tags of packages. """

    create_user(session)
    user_toshio = model.FASUser.by_name(session, 'toshio')
    user_kevin = model.FASUser.by_name(session, 'kevin')

    fedoratagger.lib.add_vote(session, 'guake', u'gnóme', True,
                                 user_toshio)
    fedoratagger.lib.add_vote(session, 'guake', 'terminal', False,
                                 user_toshio)
    fedoratagger.lib.add_tag(session, 'geany', 'ide', True,
                                user_kevin)

    session.commit()

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Modeltests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
