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

from werkzeug import wrappers
import unittest
import sys
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import taggerapi
import taggerapi.taggerlib
from taggerapi.taggerlib import model
from tests import Modeltests, create_package, create_tag, \
                  create_vote, create_rating



# pylint: disable=E1103
class Flasktests(Modeltests):
    """ Flask application tests. """

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(Flasktests, self).setUp()

        taggerapi.APP.config['TESTING'] = True
        taggerapi.SESSION = self.session
        self.app = taggerapi.APP.test_client()

    def test_pkg_get(self):
        """ Test the pkg_get function.  """

        output = self.app.get('/guake')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/guake/')
        self.assertEqual(output.status_code, 404)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  "error":'
                         ' "Package \\"guake\\" not found"\n}')

        create_package(self.session)

        output = self.app.get('/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "rating": -1.0,\n '
        ' "icon": "/packages/images/icons/__no_xapian_available__.png",\n'
        '  "summary": "drop-down terminal for gnome",\n  "name": "guake",\n'
        '  "tags": []\n}')

    def test_tag_get(self):
        """ Test the tag_pkg_get function.  """

        output = self.app.get('/tag/guake')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/tag/guake/')
        self.assertEqual(output.status_code, 404)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  "error":'
                         ' "Package \\"guake\\" not found"\n}')

        create_package(self.session)

        output = self.app.get('/tag/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "name": "guake",\n  "tags": []\n}')

        create_tag(self.session)

        output = self.app.get('/tag/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "name": "guake",\n  "tags": '
        '[\n    {\n      "total": 1,\n      "dislike": 0,\n      "tag": '
        '"gnome",\n      "votes": 1,\n      "like": 1\n    },\n    {\n  '
        '    "total": 1,\n      "dislike": 0,\n      "tag": "terminal",\n'
        '      "votes": 1,\n      "like": 1\n    }\n  ]\n}')

    def test_tag_put(self):
        """ Test the tag_pkg_put function.  """

        data = {'pkgname': 'guake', 'tags': 'terminal'}

        output = self.app.put('/tag/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "tag: This field is required."\n  ],\n  '
        '"error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'tag': 'terminal'}

        output = self.app.put('/tag/guake', data=data)
        self.assertEqual(output.status_code, 301)

        output = self.app.put('/tag/guake/', data=data)
        self.assertEqual(output.status_code, 404)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  "error":'
                         ' "Package \\"guake\\" not found"\n}')

        create_package(self.session)

        wrappers.BaseRequest.remote_addr = 'test'

        output = self.app.put('/tag/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n  "messages":'
        ' [\n    "Tag \\"terminal\\" added to the package \\"guake\\""\n'
        '  ]\n}')

        output = self.app.put('/tag/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error": "This tag is already associated to this package"\n}')

        wrappers.BaseRequest.remote_addr = 'test2'
        data = {'pkgname': 'guake', 'tag': 'terminal,, gnome'}

        output = self.app.put('/tag/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n  '
        '"messages": [\n    "Tag \\"terminal\\" added to the package '
        '\\"guake\\"",\n    "Tag \\"gnome\\" added to the package '
        '\\"guake\\""\n  ]\n}')

        output = self.app.get('/tag/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "name": "guake",\n  "tags": '
        '[\n    {\n      "total": 1,\n      "dislike": 0,\n      "tag": '
        '"gnome",\n      "votes": 1,\n      "like": 1\n    },\n    '
        '{\n      "total": 2,\n      "dislike": 0,\n      "tag": '
        '"terminal",\n      "votes": 2,\n      "like": 2\n    }\n  ]\n}')

    def test_rating_get(self):
        """ Test the rating_pkg_get function.  """

        output = self.app.get('/rating/guake')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/rating/guake/')
        self.assertEqual(output.status_code, 404)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  "error":'
                         ' "Package \\"guake\\" not found"\n}')

        create_package(self.session)

        output = self.app.get('/rating/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "rating": -1.0,\n  "name": "guake"\n}')

        create_rating(self.session)

        output = self.app.get('/rating/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "rating": 75.0,\n  "name": "guake"\n}')


    def test_rating_put(self):
        """ Test the rating_pkg_put function.  """

        data = {'pkgname': 'guake', 'ratings': 1}

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "rating: This field is required."\n  ],\n  '
        '"error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'rating': '110'}

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "rating: Input is not a percentage"\n  ],'
        '\n  "error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'rating': '-1'}

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "rating: Input is not a percentage"\n  ],'
        '\n  "error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'rating': 'asd'}

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "rating: This field is required."\n  ],'
        '\n  "error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'rating': 100}

        output = self.app.put('/rating/guake', data=data)
        self.assertEqual(output.status_code, 301)

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 404)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  "error":'
                         ' "Package \\"guake\\" not found"\n}')

        create_package(self.session)

        wrappers.BaseRequest.remote_addr = 'test'

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n '
        ' "messages": [\n    "Rating \\"100\\" added to the package '
        '\\"guake\\""\n  ]\n}')

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error": "You have already rated this package"\n}')

        wrappers.BaseRequest.remote_addr = 'test2'
        data = {'pkgname': 'guake', 'rating': 50}

        output = self.app.put('/rating/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n '
        ' "messages": [\n    "Rating \\"50\\" added to the package '
        '\\"guake\\""\n  ]\n}')

        output = self.app.get('/rating/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "rating": 75.0,\n  "name": "guake"\n}')


    def test_vote_put(self):
        """ Test the vote_tag_pkg_put function.  """

        ### Test with wrong input
        data = {'pkgname': 'guake', 'tags': 'terminal', 'vote':'1'}

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "tag: This field is required."\n  ],\n  '
        '"error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': '110'}

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "vote: Input must be either -1 (dislike) '
        'or 1 (like"\n  ],\n  "error": "Invalid input submitted"\n}')

        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': 'as'}

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error_detail": [\n    "vote: This field is required."\n  ],\n  '
        '"error": "Invalid input submitted"\n}')

        ### Test with right input format but non-existing package
        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': '-1'}

        output = self.app.put('/vote/guake', data=data)
        self.assertEqual(output.status_code, 301)

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        self.assertEqual(output.data, '{\n  "output": "notok",\n  '
        '"error": "This tag could not be found associatedto this package"\n}')

        create_package(self.session)
        create_tag(self.session)

        ### Test actual action
        wrappers.BaseRequest.remote_addr = 'test'

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n  '
        '"messages": [\n    "Vote added to the tag \\"terminal\\"'
        ' of the package \\"guake\\""\n  ]\n}')

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n  '
        '"messages": [\n    "Your vote on the tag \\"terminal\\" for '
        'the package \\"guake\\" did not changed"\n  ]\n}')

        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': '1'}

        output = self.app.put('/vote/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "output": "ok",\n  '
        '"messages": [\n    "Vote changed to the tag \\"terminal\\" of '
        'the package \\"guake\\""\n  ]\n}')

        output = self.app.get('/tag/guake/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '{\n  "name": "guake",\n  "tags": '
        '[\n    {\n      "total": 1,\n      "dislike": 0,\n      "tag": '
        '"gnome",\n      "votes": 1,\n      "like": 1\n    },\n    '
        '{\n      "total": 2,\n      "dislike": 0,\n      "tag": '
        '"terminal",\n      "votes": 2,\n      "like": 2\n    }\n  ]\n}')

    def test_api(self):
        """ Test the front page """
        output = self.app.get('/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<title> API documentation  - Tagger API</title>'
                        in output.data)

    def test_tag_dump(self):
        """ Test tag_pkg_dump """
        output = self.app.get('/tag/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '')

        create_package(self.session)
        create_tag(self.session)

        output = self.app.get('/tag/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, 'guake\tgnome\n'
        'guake\tterminal\n'
        'geany\tide\n')

    def test_rating_dump(self):
        """ Test rating_pkg_dump """
        output = self.app.get('/rating/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '')

        create_package(self.session)
        create_rating(self.session)

        output = self.app.get('/rating/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, 'guake\t75.0\n'
        'geany\t100.0')


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Flasktests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
