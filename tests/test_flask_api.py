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

__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

import base64
import json
import unittest
import tempfile
import sqlite3
import os
import sys
from werkzeug import wrappers

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import fedoratagger
import fedoratagger.lib
from fedoratagger.lib import model
from tests import (
    Modeltests,
    FakeUser,
    create_package,
    create_tag,
    create_vote,
    create_rating,
    create_user,
    set_usages,
)


# pylint: disable=E1103
class Flasktests(Modeltests):
    """ Flask application tests. """

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(Flasktests, self).setUp()

        fedoratagger.APP.config['TESTING'] = True
        fedoratagger.SESSION = self.session
        fedoratagger.api.SESSION = self.session
        self.app = fedoratagger.APP.test_client()
        wrappers.BaseRequest.remote_addr = '1.2.3'
        user = FakeUser()
        self.infos = None

    def request_with_auth(self, url, method, data):
        """ Make request to the specified url with the specified http
        method with the Authorization header.
        """
        auth = base64.b64encode(self.infos['name'] + ':' + self.infos['token'])
        return self.app.open(url,
                             method=method,
                             headers={'Authorization': 'Basic ' + auth},
                             data=data
                             )

    def test_pkg_get(self):
        """ Test the pkg_get function.  """

        output = self.app.get('/api/v1/guake')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/v1/guake/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_package(self.session)

        output = self.app.get('/api/v1/guake/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['name'], 'guake')
        self.assertEqual(output['summary'], u'drop-down terminal for gnóme')
        self.assertEqual(output['icon'],'https://apps.fedoraproject.org/'
                         'packages/images/icons/guake.png')
        self.assertEqual(output['rating'], -1)
        self.assertEqual(output['usage'], 0)
        self.assertEqual(output['tags'], [])

    def test_pkg_get_tag(self):
        """ Test the pkg_get_tag function.  """

        output = self.app.get('/api/v1/guake/tag')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/v1/guake/tag/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_package(self.session)

        output = self.app.get('/api/v1/guake/tag/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['name'], 'guake')
        self.assertEqual(output['tags'], [])

        create_tag(self.session)

        output = self.app.get('/api/v1/guake/tag/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['name'], 'guake')
        self.assertEqual(output['tags'][0]['tag'], u'gnóme')
        self.assertEqual(output['tags'][0]['votes'], 2)
        self.assertEqual(output['tags'][0]['like'], 2)
        self.assertEqual(output['tags'][0]['dislike'], 0)
        self.assertEqual(output['tags'][1]['tag'], 'terminal')
        self.assertEqual(output['tags'][0]['votes'], 2)
        self.assertEqual(output['tags'][0]['like'], 2)
        self.assertEqual(output['tags'][0]['dislike'], 0)

    def test_tag_get(self):
        """ Test the tag_get function.  """

        output = self.app.get(u'/api/v1/tag/gnóme')
        self.assertEqual(output.status_code, 301)

        output = self.app.get(u'/api/v1/tag/gnóme/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], u'Tag "gnóme" not found')

        create_package(self.session)
        create_tag(self.session)

        output = self.app.get(u'/api/v1/tag/gnóme/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['tag'], u'gnóme')
        self.assertEqual(len(output['packages']), 2)
        self.assertEqual(output['packages'][0]['package'], 'guake')

    def test_tag_put(self):
        """ Test the tag_pkg_put function.  """

        data = {'pkgname': 'guake', 'tags': 'terminal'}

        output = self.app.put('/api/v1/tag/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'][0], 'tag: This field is required.')

        data = {'pkgname': 'guake', 'tag': 'terminal'}

        output = self.app.put('/api/v1/tag/guake', data=data)
        self.assertEqual(output.status_code, 301)

        output = self.app.put('/api/v1/tag/guake/', data=data)
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_package(self.session)

        output = self.app.put('/api/v1/tag/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'][0],
                          'Tag "terminal" added to the package "guake"')
        self.assertEqual(output['user']['username'], 'anonymous')

        output = self.app.put('/api/v1/tag/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'],
                         'This tag is already associated to this package')

        data = {'pkgname': 'guake', 'tag': u'terminal,, gnóme'}

        create_user(self.session)
        user = model.FASUser.by_name(self.session, 'pingou')
        self.infos = fedoratagger.lib.get_api_token(self.session, user)
        self.infos['token'] = 'fake'

        output = self.request_with_auth('/api/v1/tag/guake/', 'PUT',
                                        data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Login invalid/expired')

        self.infos = fedoratagger.lib.get_api_token(self.session, user)

        output = self.request_with_auth('/api/v1/tag/guake/', 'PUT',
                                        data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'][0],
                          'Tag "terminal" added to the package "guake"')
        self.assertEqual(output['messages'][1],
                          u'Tag "gnóme" added to the package "guake"')

        output = self.app.get('/api/v1/guake/tag/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['name'], 'guake')
        self.assertEqual(output['tags'][0]['tag'], u'gnóme')
        self.assertEqual(output['tags'][0]['votes'], 1)
        self.assertEqual(output['tags'][0]['like'], 1)
        self.assertEqual(output['tags'][0]['dislike'], 0)
        self.assertEqual(output['tags'][1]['tag'], 'terminal')
        self.assertEqual(output['tags'][1]['votes'], 2)
        self.assertEqual(output['tags'][1]['like'], 2)
        self.assertEqual(output['tags'][1]['dislike'], 0)

        #This tests that invalid tags are rejected.
        data = {'pkgname': 'guake', 'tag': 'ass'}

        output = self.app.put('/api/v1/tag/guake/', data=data)
        self.assertEqual(output.status_code, 406)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')

    def test_pkg_get_rating(self):
        """ Test the pkg_get_rating function.  """

        output = self.app.get('/api/v1/guake/rating')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/v1/guake/rating/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_package(self.session)

        output = self.app.get('/api/v1/guake/rating/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['rating'], -1.0)
        self.assertEqual(output['name'], 'guake')

        create_rating(self.session)

        output = self.app.get('/api/v1/guake/rating/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['rating'], 75.0)
        self.assertEqual(output['name'], 'guake')

    def test_pkg_get_usage(self):
        """ Test the pkg_get_usage function.  """

        output = self.app.get('/api/v1/guake/usage')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/v1/guake/usage/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_user(self.session)
        create_package(self.session)

        output = self.app.get('/api/v1/guake/usage/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['name'], 'guake')
        self.assertEqual(output['usage'], 0)

        # Mark two people as using it.
        set_usages(self.session, usage=True)

        output = self.app.get('/api/v1/guake/usage/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['usage'], 2)
        self.assertEqual(output['name'], 'guake')

        # And now have them no longer use it.
        set_usages(self.session, usage=False)

        output = self.app.get('/api/v1/guake/usage/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['usage'], 0)
        self.assertEqual(output['name'], 'guake')

        # But if we try to mark this twice, it only counts once.
        set_usages(self.session, usage=True)
        set_usages(self.session, usage=True)
        set_usages(self.session, usage=True)

        output = self.app.get('/api/v1/guake/usage/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['usage'], 2)
        self.assertEqual(output['name'], 'guake')

    def test_pkg_ratings(self):
        """ Test the pkg_ratings function.  """

        output = self.app.get('/api/v1/ratings/guake')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/v1/ratings/guake/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_package(self.session)

        output = self.app.get('/api/v1/ratings/guake,geany/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(len(output['ratings']), 2)
        self.assertEqual(output['ratings'][0]['rating'], -1)
        self.assertEqual(output['ratings'][0]['name'], 'guake')
        self.assertEqual(output['ratings'][1]['rating'], -1)
        self.assertEqual(output['ratings'][1]['name'], 'geany')

        create_rating(self.session)

        output = self.app.get('/api/v1/ratings/guake,geany/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(len(output['ratings']), 2)
        self.assertEqual(output['ratings'][0]['name'], 'guake')
        self.assertEqual(output['ratings'][0]['rating'], 75)
        self.assertEqual(output['ratings'][1]['name'], 'geany')
        self.assertEqual(output['ratings'][1]['rating'], 100.0)

    def test_rating_get(self):
        """ Test the rating_get function.  """

        output = self.app.get('/api/v1/rating/75')
        self.assertEqual(output.status_code, 301)

        output = self.app.get('/api/v1/rating/76/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'],
                         'No packages found with rating "76.0"')

        output = self.app.get('/api/v1/rating/as/')
        self.assertEqual(output.status_code, 500)

        create_package(self.session)
        create_rating(self.session)

        output = self.app.get('/api/v1/rating/75/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['rating'], 75)
        self.assertEqual(len(output['packages']), 1)
        self.assertEqual(output['packages'][0], 'guake')

    def test_rating_put(self):
        """ Test the rating_pkg_put function.  """

        data = {'pkgname': 'guake', 'ratings': 1}

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ["rating: This field is required."])

        data = {'pkgname': 'guake', 'rating': '110'}

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ["rating: Input is not a percentage"])

        data = {'pkgname': 'guake', 'rating': '-1'}

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ["rating: Input is not a percentage"])

        data = {'pkgname': 'guake', 'rating': 'asd'}

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ["rating: This field is required."])

        data = {'pkgname': 'guake', 'rating': 100}

        output = self.app.put('/api/v1/rating/guake', data=data)
        self.assertEqual(output.status_code, 301)

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Package "guake" not found')

        create_package(self.session)

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'], [
                         'Rating "100" added to the package "guake"'])

        output = self.app.put('/api/v1/rating/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'], [
                        'Rating on package "guake" did not change'])

        data = {'pkgname': 'guake', 'rating': 50}
        create_user(self.session)
        user = model.FASUser.by_name(self.session, 'pingou')
        self.infos = fedoratagger.lib.get_api_token(self.session, user)

        output = self.request_with_auth('/api/v1/rating/guake/', 'PUT', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'], [
                         'Rating "50" added to the package "guake"'])

        output = self.app.get('/api/v1/guake/rating/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['rating'], 75.0)
        self.assertEqual(output['name'], 'guake')

    def test_vote_put(self):
        """ Test the vote_tag_pkg_put function.  """

        ### Test with wrong input
        data = {'pkgname': 'guake', 'tags': 'terminal', 'vote':'1'}

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ["tag: This field is required."])

        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': '110'}

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ['vote: Input must be either -1 (dislike) '
        'or 1 (like)'])

        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': 'as'}

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'Invalid input submitted')
        self.assertEqual(output['error_detail'],
                         ["vote: This field is required."])

        ### Test with right input format but non-existing package
        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': '-1'}

        output = self.app.put('/api/v1/vote/guake', data=data)
        self.assertEqual(output.status_code, 301)

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 500)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'This tag could not be found '
                        'associated to this package')

        create_package(self.session)
        create_tag(self.session)

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'], ['Vote added on the tag "terminal"'
        ' of the package "guake"'])

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'], ['Your vote on the tag '
                                              '"terminal" for the package'
                                              ' "guake" did not change'])

        data = {'pkgname': 'guake', 'tag': 'terminal', 'vote': '1'}

        output = self.app.put('/api/v1/vote/guake/', data=data)
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(output['messages'], ['Vote changed on the tag '
                                              '"terminal" of the package'
                                              ' "guake"'])

        output = self.app.get('/api/v1/guake/tag/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output['name'], 'guake')
        self.assertEqual(output['tags'][0]['tag'], u'gnóme')
        self.assertEqual(output['tags'][0]['votes'], 2)
        self.assertEqual(output['tags'][0]['like'], 2)
        self.assertEqual(output['tags'][0]['dislike'], 0)
        self.assertEqual(output['tags'][1]['tag'], 'terminal')
        self.assertEqual(output['tags'][1]['votes'], 3)
        self.assertEqual(output['tags'][1]['like'], 3)
        self.assertEqual(output['tags'][1]['dislike'], 0)

    def test_api(self):
        """ Test the front page """
        output = self.app.get('/api/v1/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<title> API documentation  - Tagger API</title>'
                        in output.data)

    def test_tag_dump(self):
        """ Test tag_pkg_dump """
        output = self.app.get('/api/v1/tag/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '')

        create_package(self.session)
        create_tag(self.session)

        output = self.app.get('/api/v1/tag/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data.decode('utf-8'), u'guake\tgnóme\n'
        u'guake\tterminal\n'
        u'geany\tgnóme\ngeany\tide')

    def test_tag_export(self):
        """ Test tag_pkg_export.

        A backwards compat url for fedora-packages' cronjob.
        """
        output = self.app.get('/api/v1/tag/export/')
        self.assertEqual(output.status_code, 200)
        target = {'packages': []}
        self.assertEqual(json.loads(output.data), target)

        create_package(self.session)
        create_tag(self.session)

        output = self.app.get('/api/v1/tag/export/')
        self.assertEqual(output.status_code, 200)
        target = {
            u'packages': [
                {
                    u'guake': [{
                        u'tag': u'gnóme',
                        u'total': 2,
                    },{
                        u'tag': u'terminal',
                        u'total': 2,
                    }]
                }, {
                    u'geany': [{
                        u'tag': u'gnóme',
                        u'total': 2,
                    },{
                        u'tag': u'ide',
                        u'total': 2,
                    }]
                }, {
                    u'gitg': [],
                }
            ]
        }
        self.assertEqual(json.loads(output.data), target)

    def test_tag_sqlite(self):
        """ Test tag_pkg_sqlite.

        A url for bodhi's masher.
        """
        create_package(self.session)
        create_tag(self.session)

        output = self.app.get('/api/v1/tag/sqlitebuildtags/')
        self.assertEqual(output.status_code, 200)

        fd, db_filename = tempfile.mkstemp()
        os.close(fd)

        with open(db_filename, 'w') as f:
            f.write(output.data)

        with sqlite3.connect(db_filename) as conn:
            cursor = conn.cursor();
            cursor.execute("select * from packagetags;")
            rows = cursor.fetchall()

        target_rows = [
            (u'guake', u'gnóme', 2),
            (u'guake', u'terminal', 2),
            (u'geany', u'gnóme', 2),
            (u'geany', u'ide', 2),
        ]
        self.assertEqual(len(rows), len(target_rows))
        for actual, target in zip(rows, target_rows):
            self.assertEqual(actual, target)

    def test_rating_dump(self):
        """ Test rating_pkg_dump """
        output = self.app.get('/api/v1/rating/dump/')
        self.assertEqual(output.status_code, 200)
        self.assertEqual(output.data, '')

        create_package(self.session)
        create_rating(self.session)

        output = self.app.get('/api/v1/rating/dump/')
        self.assertEqual(output.status_code, 200)
        expected = 'guake\t75.0\t2\t0\ngeany\t100.0\t1\t0'
        self.assertEqual(output.data, expected)

    def test_random(self):
        """ Test pkg_random """
        output = self.app.get('/api/v1/random/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'No package could be found')

        create_package(self.session)
        create_rating(self.session)

        output = self.app.get('/api/v1/random/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        keys = output.keys()
        keys.sort()
        self.assertEqual(set(output.keys()), set([
            'rating', 'summary', 'name', 'tags', 'usage', 'icon',
        ]))

    def test_statistics(self):
        """ Test statistics """
        output = self.app.get('/api/v1/statistics/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(), ['summary'])
        self.assertEqual(0, output['summary']['with_tags'])
        self.assertEqual(0, output['summary']['no_tags'])
        self.assertEqual(0, output['summary']['tags_per_package'])
        self.assertEqual(0, output['summary']['tags_per_package_no_zeroes'])
        self.assertEqual(0, output['summary']['total_packages'])
        self.assertEqual(0, output['summary']['total_unique_tags'])

        create_package(self.session)

        output = self.app.get('/api/v1/statistics/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual([ 'summary'], output.keys())
        self.assertEqual(0, output['summary']['with_tags'])
        self.assertEqual(3, output['summary']['no_tags'])
        self.assertEqual(0, output['summary']['tags_per_package'])
        self.assertEqual(0, output['summary']['tags_per_package_no_zeroes'])
        self.assertEqual(3, output['summary']['total_packages'])
        self.assertEqual(0, output['summary']['total_unique_tags'])

        create_tag(self.session)

        output = self.app.get('/api/v1/statistics/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(['summary'], output.keys())
        self.assertEqual(2, output['summary']['with_tags'])
        self.assertEqual(1, output['summary']['no_tags'])
        self.assertEqual(4/float(3), output['summary']['tags_per_package'])
        self.assertEqual(2, output['summary']['tags_per_package_no_zeroes'])
        self.assertEqual(3, output['summary']['total_packages'])
        self.assertEqual(3, output['summary']['total_unique_tags'])

    def test_leaderboard(self):
        """ Test leaderboard """
        output = self.app.get('/api/v1/leaderboard/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(), [])

        create_package(self.session)
        create_tag(self.session)

        output = self.app.get('/api/v1/leaderboard/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(), ['1', '3', '2', '5', '4', '6'])
        self.assertEqual(output['1'].keys(), ['score', 'gravatar', 'name'])
        self.assertEqual(output['1']['name'], 'pingou')
        self.assertEqual(output['1']['score'], 8)
        self.assertEqual(output['2']['name'], 'toshio')
        self.assertEqual(output['2']['score'], 2)
        self.assertEqual(output['5']['name'], 'ralph')

    def test_score(self):
        """ Test the scores """
        output = self.app.get('/api/v1/score/pingou/')
        self.assertEqual(output.status_code, 404)
        output = json.loads(output.data)
        self.assertEqual(output.keys(), ['output', 'error'])
        self.assertEqual(output['output'], 'notok')
        self.assertEqual(output['error'], 'User not found')

        create_package(self.session)
        create_tag(self.session)

        output = self.app.get('/api/v1/score/pingou/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(), ['score', 'gravatar', 'name'])
        self.assertEqual(output['name'], 'pingou')
        self.assertEqual(output['score'], 8)

        output = self.app.get('/api/v1/score/toshio/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(), ['score', 'gravatar', 'name'])
        self.assertEqual(output['name'], 'toshio')
        self.assertEqual(output['score'], 2)

    def test_login(self):
        """ Test the login page """
        output = self.app.get('/api/v1/login/')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<title>OpenID transaction in progress</title>'
                        in output.data)

        output = self.app.get('/api/v1/login/?next=test')
        self.assertEqual(output.status_code, 200)
        self.assertTrue('<title>OpenID transaction in progress</title>'
                        in output.data)

    def test_token(self):
        """ Test the token page """
        output = self.app.get('/api/v1/token/')
        self.assertEqual(output.status_code, 302)

        ## We need to figure out a way to shortcut the @login_required
        ## so that we can actually test the rest
        #output = json.loads(output.data)
        #self.assertEqual(output.keys(), ['token', 'name'])
        #self.assertEqual(output['name'], '1.2.3')
        #self.assertTrue(output['token'].startswith('dGFnZ2VyYXBp#'))

    def test_toggle(self):
        """Test that toggle function reverses input"""
        response = self.app.get('/notifs_state/')
        self.assertEqual(response.status_code, 200)
        old_data = json.loads(response.data)
        old_state = old_data['notifications_on']
        new_response = self.app.get('/notifs_toggle/')
        self.assertEqual(new_response.status_code, 200)
        data = json.loads(new_response.data)
        new_state = data['notifications_on']
        if old_state == False:
            self.assertEqual(new_state, True)
        elif old_state == True:
            self.assertEqual(new_state, False)
        else:
            self.assertEqual(1, 2)

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Flasktests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
