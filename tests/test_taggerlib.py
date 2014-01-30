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
fedoratagger tests lib.
'''

__requires__ = ['SQLAlchemy >= 0.7']
import pkg_resources

import unittest
import sys
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import fedoratagger.lib
from fedoratagger.lib import model
from tests import Modeltests, FakeUser, create_package, create_tag, \
                  create_user


class TaggerLibtests(Modeltests):
    """ TaggerLib tests. """

    def test_init_package(self):
        """ Test the __init__ function of Package. """
        create_package(self.session)
        self.assertEqual(3, len(model.Package.all(self.session)))

    def test_add_rating(self):
        """ Test the add_rating function of taggerlib. """
        create_user(self.session)
        user_pingou = model.FASUser.by_name(self.session, 'pingou')
        user_ralph = model.FASUser.by_name(self.session, 'ralph')

        create_package(self.session)
        out = fedoratagger.lib.add_rating(self.session, 'guake', 100,
                                             user_pingou)
        self.assertEqual(out, 'Rating "100" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        rating = model.Rating.rating_of_package(self.session, pkg.id)
        self.assertEqual(100, rating)

        out = fedoratagger.lib.add_rating(self.session, 'guake', 50,
                                          user_pingou)
        self.assertEqual(out, 'Rating on package "guake" changed to "50"')
        self.session.commit()
        out = fedoratagger.lib.add_rating(self.session, 'guake', 50,
                                          user_pingou)
        self.assertEqual(out, 'Rating on package "guake" did not change')
        self.session.commit()

        out = fedoratagger.lib.add_rating(self.session, 'guake', 100,
                                          user_ralph)
        self.assertEqual(out, 'Rating "100" added to the package "guake"')
        self.session.commit()

        rating = model.Rating.rating_of_package(self.session, pkg.id)
        self.assertEqual(75, rating)

        r = fedoratagger.lib.model.Package.rating(pkg, self.session)
        self.assertEquals(75, r)

    def test_add_tag(self):
        """ Test the add_tag function of taggerlib. """
        create_user(self.session)
        user_pingou = model.FASUser.by_name(self.session, 'pingou')
        user_ralph = model.FASUser.by_name(self.session, 'ralph')

        create_package(self.session)

        out = fedoratagger.lib.add_tag(self.session, 'guake', u'gnóme',
                                          user_pingou)
        self.assertEqual(out, u'Tag "gnóme" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(1, len(pkg.tags))
        self.assertEqual(u'gnóme', pkg.tags[0].label)

        self.assertRaises(IntegrityError,
                          fedoratagger.lib.add_tag,
                          self.session, 'guake', u'gnóme', user_pingou)
        self.session.rollback()

        out = fedoratagger.lib.add_tag(self.session, 'guake', 'terminal',
                                          user_pingou)
        self.assertEqual(out, 'Tag "terminal" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(2, len(pkg.tags))
        self.assertEqual(u'gnóme', pkg.tags[0].label)
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(1, pkg.tags[1].like)

        out = fedoratagger.lib.add_tag(self.session, 'guake', 'terminal',
                                          user_ralph)
        self.assertEqual(out, 'Tag "terminal" added to the package "guake"')
        self.session.commit()

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(2, len(pkg.tags))
        self.assertEqual(u'gnóme', pkg.tags[0].label)
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(2, pkg.tags[1].like)

        self.assertRaises(ValueError,
                          fedoratagger.lib.add_tag,
                          self.session, 'guake', 'ass',
                          user_pingou)

        tagobj1 = model.Tag.get(self.session, pkg.id, 'terminal')
        self.assertEquals('terminal on guake', tagobj1.__unicode__())
        tagobj2 = model.Tag.get(self.session, pkg.id, u'gnóme')
        self.assertEquals(u'gnóme on guake', tagobj2.__unicode__())

    def test_banned(self):
        """ Test the banned property of a Tag"""
        create_user(self.session)
        user_pingou = model.FASUser.by_name(self.session, 'pingou')
        create_package(self.session)
        pkg = model.Package.by_name(self.session, 'guake')
        out = fedoratagger.lib.add_tag(self.session, 'guake', 'X-test',
                                       user_pingou)
        self.assertEqual(out, 'Tag "x-test" added to the package "guake"')

        tagobj = model.Tag.get(self.session, pkg.id, 'x-test')
        self.assertEquals(True, tagobj.banned)
        out = fedoratagger.lib.add_tag(self.session, 'guake',
                                       'terminal',
                                       user_pingou)
        self.assertEqual(out, 'Tag "terminal" added to the package "guake"')
        tagobj = model.Tag.get(self.session, pkg.id, 'terminal')
        self.assertEquals(False, tagobj.banned)
        out = fedoratagger.lib.add_tag(self.session, 'guake',
                                       'application',
                                       user_pingou)
        self.assertEqual(out, 'Tag "application" added to the package "guake"')
        tagobj = model.Tag.get(self.session, pkg.id, 'application')
        self.assertEquals(True, tagobj.banned)

    def test_tag_sorter(self):
        """ Test the tag_sorter function of model. """
        self.test_add_tag()

        pkg = model.Package.by_name(self.session, 'guake')

        tagobj1 = model.Tag.get(self.session, pkg.id, 'terminal')
        tagobj2 = model.Tag.get(self.session, pkg.id, u'gnóme')
        result = fedoratagger.lib.model.tag_sorter(tagobj1,
                                                   tagobj2)

        self.assertEqual(1, result)

        result = fedoratagger.lib.model.tag_sorter(tagobj1,
                                                   tagobj1)
        self.assertEquals(0, result)

        result = fedoratagger.lib.model.tag_sorter(tagobj2,
                                                   tagobj1)

        self.assertEqual(-1, result)

    def test_rank_changes(self):
        """ Test that user rank changes appropriately. """
        self.test_add_tag()
        user_pingou = model.FASUser.by_name(self.session, 'pingou')
        user_toshio = model.FASUser.by_name(self.session, 'toshio')
        user_kevin = model.FASUser.by_name(self.session, 'kevin')

        self.assertEqual(user_pingou.rank(self.session), 1)
        self.assertEqual(user_toshio.rank(self.session), 3)
        self.assertEqual(user_kevin.rank(self.session), 3)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                        'terminal', True , user_pingou)

        self.assertEqual(user_pingou.rank(self.session), 1)
        self.assertEqual(user_toshio.rank(self.session), 3)
        self.assertEqual(user_kevin.rank(self.session), 3)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                           'terminal', True , user_toshio)

        self.assertEqual(user_pingou.rank(self.session), 1)
        self.assertEqual(user_toshio.rank(self.session), 3)
        self.assertEqual(user_kevin.rank(self.session), 4)

        user = model.FASUser(username='anonymous',
                             email='anonymous@p.o',
                             anonymous=True)
        self.assertEqual(user.rank(self.session), -1)

    def test_add_vote(self):
        """ Test the add_vote function of taggerlib. """
        self.test_add_tag()

        user_pingou = model.FASUser.by_name(self.session, 'pingou')
        user_toshio = model.FASUser.by_name(self.session, 'toshio')
        user_kevin = model.FASUser.by_name(self.session, 'kevin')

        self.assertRaises(fedoratagger.lib.TaggerapiException,
                          fedoratagger.lib.add_vote,
                          self.session, 'test', 'terminal', True ,
                          user_pingou)

        self.assertRaises(fedoratagger.lib.TaggerapiException,
                          fedoratagger.lib.add_vote,
                          self.session, 'guake', 'test', True ,
                          user_pingou)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                           'terminal', True , user_pingou)
        self.assertEqual(out, 'Your vote on the tag "terminal" for the '
                         'package "guake" did not change')

        pkg = model.Package.by_name(self.session, 'guake')
        self.assertEqual(2, len(pkg.tags))
        self.assertEqual(u'gnóme', pkg.tags[0].label)
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(2, pkg.tags[1].like)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                           'terminal', False ,
                                           user_pingou)
        self.assertEqual(out, 'Vote changed on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(1, pkg.tags[1].like)
        self.assertEqual(1, pkg.tags[1].dislike)
        self.assertEqual(0, pkg.tags[1].total)
        self.assertEqual(2, pkg.tags[1].total_votes)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                           'terminal', True , user_toshio)
        self.assertEqual(out, 'Vote added on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(2, pkg.tags[1].like)
        self.assertEqual(1, pkg.tags[1].dislike)
        self.assertEqual(1, pkg.tags[1].total)
        self.assertEqual(3, pkg.tags[1].total_votes)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                           'terminal', True , user_pingou)
        self.assertEqual(out, 'Vote changed on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(3, pkg.tags[1].like)
        self.assertEqual(0, pkg.tags[1].dislike)
        self.assertEqual(3, pkg.tags[1].total)
        self.assertEqual(3, pkg.tags[1].total_votes)

        out = fedoratagger.lib.add_vote(self.session, 'guake',
                                           'terminal', False , user_kevin)
        self.assertEqual(out, 'Vote added on the tag "terminal" of the'
                         ' package "guake"')

        self.assertEqual(2, len(pkg.tags))
        self.assertEqual('terminal', pkg.tags[1].label)
        self.assertEqual(1, pkg.tags[0].like)
        self.assertEqual(3, pkg.tags[1].like)
        self.assertEqual(1, pkg.tags[1].dislike)
        self.assertEqual(2, pkg.tags[1].total)
        self.assertEqual(4, pkg.tags[1].total_votes)

    def test_statistics(self):
        """ Test the statistics method. """
        out = fedoratagger.lib.statistics(self.session)
        self.assertEqual(['summary'], out.keys())
        self.assertEqual(0, out['summary']['with_tags'])
        self.assertEqual(0, out['summary']['no_tags'])
        self.assertEqual(0, out['summary']['tags_per_package'])
        self.assertEqual(0, out['summary']['tags_per_package_no_zeroes'])
        self.assertEqual(0, out['summary']['total_packages'])
        self.assertEqual(0, out['summary']['total_unique_tags'])

        create_package(self.session)
        out = fedoratagger.lib.statistics(self.session)
        self.assertEqual(['summary'], out.keys())
        self.assertEqual(0, out['summary']['with_tags'])
        self.assertEqual(3, out['summary']['no_tags'])
        self.assertEqual(0, out['summary']['tags_per_package'])
        self.assertEqual(0, out['summary']['tags_per_package_no_zeroes'])
        self.assertEqual(3, out['summary']['total_packages'])
        self.assertEqual(0, out['summary']['total_unique_tags'])

        create_tag(self.session)
        out = fedoratagger.lib.statistics(self.session)
        self.assertEqual(['summary'], out.keys())
        self.assertEqual(2, out['summary']['with_tags'])
        self.assertEqual(1, out['summary']['no_tags'])
        self.assertEqual(4/float(3), out['summary']['tags_per_package'])
        self.assertEqual(2, out['summary']['tags_per_package_no_zeroes'])
        self.assertEqual(3, out['summary']['total_packages'])
        self.assertEqual(3, out['summary']['total_unique_tags'])

    def test_statistics_by_user(self):
        """ Test the statistics per user method. """
        self.test_add_vote()
        user_yograterol = model.FASUser.by_name(self.session, 'yograterol')

        # Check nothing vote
        out = fedoratagger.lib.statistics_by_user(self.session,
                                                  user_yograterol)

        self.assertEqual(out["total_like"], 0)
        self.assertEqual(out["total_dislike"], 0)

        # Do a vote and generate the statistics
        fedoratagger.lib.add_vote(self.session, 'guake',
                                  'terminal', False, user_yograterol)

        out = fedoratagger.lib.statistics_by_user(self.session,
                                                  user_yograterol)
        self.assertEqual(out["total_like"], 0)
        self.assertEqual(out["total_dislike"], 1)

        self.assertEqual(out["dislike"][0][0], 'guake')
        self.assertEqual(out["dislike"][0][1], 'terminal')

        fedoratagger.lib.add_vote(self.session, 'guake',
                                  'terminal', True, user_yograterol)

        out = fedoratagger.lib.statistics_by_user(self.session,
                                                  user_yograterol)

        self.assertEqual(out["total_like"], 1)
        self.assertEqual(out["total_dislike"], 0)

        self.assertEqual(out["like"][0][0], 'guake')
        self.assertEqual(out["like"][0][1], 'terminal')

    def test_leaderboard(self):
        """ Test the leaderboard method. """
        out = fedoratagger.lib.leaderboard(self.session)
        self.assertEqual([], out.keys())

        create_package(self.session)
        create_tag(self.session)

        out = fedoratagger.lib.leaderboard(self.session)
        self.assertEqual(out.keys(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(out[1].keys(), ['score', 'gravatar', 'name'])
        self.assertEqual(out[1]['name'], 'pingou')
        self.assertEqual(out[1]['score'], 8)
        self.assertEqual(out[2]['name'], 'toshio')
        self.assertEqual(out[2]['score'], 2)

    def test_score(self):
        """ Test the score method. """
        self.assertRaises(NoResultFound,
                          fedoratagger.lib.score,
                          self.session,
                          'asd'
                          )

        create_package(self.session)
        create_tag(self.session)

        out = fedoratagger.lib.score(self.session, 'pingou')
        self.assertEqual(out.keys(), ['score', 'gravatar', 'name'])
        self.assertEqual(out['name'], 'pingou')
        self.assertEqual(out['score'], 8)

        out = fedoratagger.lib.score(self.session, 'toshio')
        self.assertEqual(out.keys(), ['score', 'gravatar', 'name'])
        self.assertEqual(out['name'], 'toshio')
        self.assertEqual(out['score'], 2)

    def test_generate_api_token(self):
        """ Test the generate_api_token method. """
        token = fedoratagger.lib.generate_api_token()
        self.assertTrue(token.startswith('dGFnZ2VyYXBp##'))
        self.assertEqual(len(token), 30)

    def test_get_api_token(self):
        """ Test the get_api_token method. """
        user = FakeUser()

        infos = fedoratagger.lib.get_api_token(self.session, user)
        self.assertEqual(infos['name'], 'fake_username')
        self.assertTrue(infos['token'].startswith('dGFnZ2VyYXBp##'))

        dbuser = model.FASUser.by_name(self.session, infos['name'])
        self.assertTrue(infos['token'], dbuser.api_token)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TaggerLibtests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
