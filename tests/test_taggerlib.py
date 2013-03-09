# -*- coding: utf-8 -*-
#
# Copyright © 2013  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

'''
taggerapi tests lib.
'''

__requires__ = ['SQLAlchemy >= 0.7']
import pkg_resources

import unittest
import sys
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import taggerapi.taggerlib
from taggerapi.taggerlib import model
from tests import Modeltests, create_package


class TaggerLibtests(Modeltests):
    """ TaggerLib tests. """

    def test_init_package(self):
        """ Test the __init__ function of Package. """
        create_package(self.session)
        self.assertEqual(3, len(model.Package.all(self.session)))

    def test_add_rating(self):
        """ Test the add_rating function of taggerlib. """
        create_package(self.session)
        out = taggerapi.taggerlib.add_rating(self.session, 'guake', 100,
                                             'pingou')
        self.assertEqual(out, 'Rating "100" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        rating = model.Rating.rating_of_package(self.session, pkg.id)
        self.assertEqual(100, rating)

        self.assertRaises(SQLAlchemyError,
                          taggerapi.taggerlib.add_rating,
                          self.session, 'guake', 50, 'pingou')
        self.session.rollback()

        out = taggerapi.taggerlib.add_rating(self.session, 'guake', 50,
                                             'ralph')
        self.assertEqual(out, 'Rating "50" added to the package "guake"')
        self.session.commit()

        rating = model.Rating.rating_of_package(self.session, pkg.id)
        self.assertEqual(75, rating)

    def test_add_tag(self):
        """ Test the add_tag function of taggerlib. """
        create_package(self.session)
        out = taggerapi.taggerlib.add_tag(self.session, 'guake', 'gnome',
                                             'pingou')
        self.assertEqual(out, 'Tag "gnome" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(1, len(pkg.tags))
        self.assertEqual('gnome', pkg.tags[0].label)

        self.assertRaises(SQLAlchemyError,
                          taggerapi.taggerlib.add_tag,
                          self.session, 'guake', 'gnome', 'pingou')
        self.session.rollback()

        out = taggerapi.taggerlib.add_tag(self.session, 'guake', 'terminal',
                                             'pingou')
        self.assertEqual(out, 'Tag "terminal" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('gnome', pkg.tags[0].label)
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(1, pkg.tags[1].like)

        out = taggerapi.taggerlib.add_tag(self.session, 'guake', 'terminal',
                                          'ralph')
        self.assertEqual(out, 'Tag "terminal" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('gnome', pkg.tags[0].label)
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(2, pkg.tags[1].like)

    def test_add_vote(self):
        """ Test the add_vote function of taggerlib. """
        self.test_add_tag()

        self.assertRaises(taggerapi.taggerlib.TaggerapiException,
                          taggerapi.taggerlib.add_vote,
                          self.session, 'test', 'terminal', True ,
                          'pingou')

        self.assertRaises(taggerapi.taggerlib.TaggerapiException,
                          taggerapi.taggerlib.add_vote,
                          self.session, 'guake', 'test', True ,
                          'pingou')

        out = taggerapi.taggerlib.add_vote(self.session, 'guake',
                                           'terminal', True , 'pingou')
        self.assertEqual(out, 'Your vote on the tag "terminal" for the '
                         'package "guake" did not changed')

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('gnome', pkg.tags[0].label)
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(2, pkg.tags[1].like)

        out = taggerapi.taggerlib.add_vote(self.session, 'guake',
                                           'terminal', False , 'pingou')
        self.assertEqual(out, 'Vote changed on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(1, pkg.tags[1].like)
        self.assertEqual(1, pkg.tags[1].dislike)
        self.assertEqual(0, pkg.tags[1].total)
        self.assertEqual(2, pkg.tags[1].total_votes)

        out = taggerapi.taggerlib.add_vote(self.session, 'guake',
                                           'terminal', True , 'toshio')
        self.assertEqual(out, 'Vote added on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(2, pkg.tags[1].like)
        self.assertEqual(1, pkg.tags[1].dislike)
        self.assertEqual(1, pkg.tags[1].total)
        self.assertEqual(3, pkg.tags[1].total_votes)

        out = taggerapi.taggerlib.add_vote(self.session, 'guake',
                                           'terminal', True , 'pingou')
        self.assertEqual(out, 'Vote changed on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(3, pkg.tags[1].like)
        self.assertEqual(0, pkg.tags[1].dislike)
        self.assertEqual(3, pkg.tags[1].total)
        self.assertEqual(3, pkg.tags[1].total_votes)

        out = taggerapi.taggerlib.add_vote(self.session, 'guake',
                                           'terminal', False , 'kevin')
        self.assertEqual(out, 'Vote added on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(3, pkg.tags[1].like)
        self.assertEqual(1, pkg.tags[1].dislike)
        self.assertEqual(2, pkg.tags[1].total)
        self.assertEqual(4, pkg.tags[1].total_votes)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TaggerLibtests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
