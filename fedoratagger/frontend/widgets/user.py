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
import tw2.core
import tw2.jquery
import hashlib

import fedora.client

import fedoratagger as ft

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
    def user(self):
        return flask.g.fas_user

    @property
    def url(self):
        return flask.request.url

    @property
    def gravatar_tag(self):
        if self.logged_in:
            return self.user.gravatar_md
        else:
            system = fedora.client.AccountSystem()
            url = system.avatar_url('anonymous-tagger', lookup_email=False)
            return "<img src='{url}' />".format(url=url)

    @property
    def formatted_name(self):
        # TODO -- real name?
        return self.user.username

    @property
    def logged_in(self):
        return self.user and not self.user.anonymous

    @property
    def username(self):
        return self.user.username

    @property
    def score(self):
        return self.user.score

    @property
    def rank(self):
        return self.user.rank(ft.SESSION)

    @property
    def notifications_on(self):
        return getattr(self.user, 'notifications_on', False) \
                and "checked='checked'" or ""

    @property
    def _notifications_on(self):
        return getattr(self.user, 'notifications_on', False) \
                and "true" or "false"
