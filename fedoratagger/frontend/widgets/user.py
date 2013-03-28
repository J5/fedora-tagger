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
import tw2.jquery
import tg
import hashlib

import fedoratagger.model as m

photo_css = tw2.core.CSSLink(link='css/photo.css')
thumbnail_js = tw2.core.JSLink(
    link='javascript/thumbnail.js',
    resources=[tw2.jquery.jquery_js],
)

class UserWidget(tw2.core.Widget):
    """ Gravatar widget """

    resources = [photo_css, thumbnail_js]
    template = 'fedoratagger.frontend.widgets.templates.user'

    @property
    def gravatar_tag(self):
        return m.get_user().gravatar_md

    @property
    def formatted_name(self):
        return tg.request.identity.get(
            'ircnick',
            self.username
        )

    @property
    def logged_in(self):
        return self.username != 'anonymous'

    @property
    def username(self):
        return m.get_user().username

    @property
    def total_votes(self):
        user = m.get_user(self.username)
        return user.total_votes

    @property
    def rank(self):
        user = m.get_user(self.username)
        return user.rank

    @property
    def notifications_on(self):
        user = m.get_user(self.username)
        return user.notifications_on and "checked='checked'" or ""

    @property
    def _notifications_on(self):
        user = m.get_user(self.username)
        return user.notifications_on and "true" or "false"
