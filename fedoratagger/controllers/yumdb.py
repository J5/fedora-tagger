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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README.rst and LICENSE files for full details of the license
# -*- coding: utf-8 -*-
""" This file contains a controller that provides a sqlite database which is
consumable by createrepo.  It is used by bodhi for mashing metadata into new
repositories.

"""

import os
import tempfile
import sqlalchemy

from tg import expose

from fedoratagger import model
from fedoratagger.lib.base import BaseController

# These are used *only* by this controller.
from fedoratagger.model.yumdb import yummeta, YumTagsTable


__all__ = ['YumDBController']


class YumDBController(BaseController):

    def _buildtags(self):
        return sum([
            [
                {
                    'name': package.name,
                    'tag': tag.label.label,
                    'score': tag.total,
                } for tag in package.tags
            ] for package in model.Package.query.all()
        ], [])

    @expose('json')
    def buildtags(self, repo):
        return dict(buildtags=self._buildtags())

    @expose(content_type='application/sqlite')
    def sqlitebuildtags(self, repo):
        '''Return a sqlite database of packagebuilds and tags.

        The database returned will contain copies or subsets of tables in
        tagger modified to be consumable by Yum.

        Bodhi downloads this and mashes it into the repositories.

        :arg repo: A repository shortname to retrieve tags for
                   (e.g. 'F-11-i386')

            - Unfortunately, tagger knows nothing about repos and so this is
              ignored.  It is retained here for the appearance of backwards
              compatibility.

        '''

        # initialize/clear database
        fd, dbfile = tempfile.mkstemp()
        os.close(fd)
        sqliteconn = 'sqlite:///%s' % dbfile

        yummeta.bind = sqlalchemy.create_engine(sqliteconn)
        yummeta.create_all()

        # since we're using two databases, we'll need a new session
        lite_session = model.sessionmaker(yummeta.bind)()

        pkg_tags = self._buildtags()

        if pkg_tags:
            # If there's no tags, we'll return an empty database
            lite_session.execute(YumTagsTable.insert(), pkg_tags)

        lite_session.commit()

        f = open(dbfile, 'r')
        dump = f.read()
        f.close()
        os.unlink(dbfile)
        return dump
