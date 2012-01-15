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
import tw2.core
import tw2.forms

import fedoratagger.model as m

voting_js = tw2.core.JSLink(link="javascript/voting.js")

class TagWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    css_class = ""
    tag = tw2.core.Param()
    template = 'fedoratagger.widgets.templates.tag'

    @property
    def upcls(self):
        user = m.get_user()
        query = m.Vote.query.filter_by(user=user, tag=self.tag)
        if query.count() == 0:
            return ""

        if not query.one().like:
            return ""

        return "mod"

    @property
    def downcls(self):
        user = m.get_user()
        query = m.Vote.query.filter_by(user=user, tag=self.tag)
        if query.count() == 0:
            return ""

        if query.one().like:
            return ""

        return "mod"

    @property
    def textcls(self):
        user = m.get_user()
        query = m.Vote.query.filter_by(user=user, tag=self.tag)
        if query.count() == 0:
            return ""

        if query.one().like:
            return "up_text"

        return "down_text"
