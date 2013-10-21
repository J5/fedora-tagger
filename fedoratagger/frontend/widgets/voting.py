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

import flask
from sqlalchemy.orm.exc import NoResultFound

import tw2.core
import tw2.forms
import tw2.jquery

import fedoratagger as ft
import fedoratagger.lib.model as m

escape_js = tw2.core.JSLink(
    link="javascript/escape.js",
)
voting_js = tw2.core.JSLink(
    link="javascript/voting.js",
    resources=[
        escape_js,
        tw2.jquery.jquery_js,
    ],
)

class TagWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    css_class = ""
    tag = tw2.core.Param()
    template = 'fedoratagger.frontend.widgets.templates.tag'

    @property
    def _like(self):
        user = flask.g.fas_user
        if not user:
            return 0

        try:
            voteobj = m.Vote.get(ft.SESSION, user_id=user.id, tag_id=self.tag.id)
        except NoResultFound:
            return 0

        if voteobj.like:
            return 1
        else:
            return -1

    @property
    def upcls(self):
        if self._like > 0:
            return "mod"
        else:
            return ""

    @property
    def downcls(self):
        if self._like < 0:
            return "mod"
        else:
            return ""

    @property
    def textcls(self):
        if self._like == 0:
            return ""
        elif self._like == 1:
            return "up_text"
        else:
            return "down_text"
