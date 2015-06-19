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
import tw2.forms
import tw2.jquery
import tw2.jqplugins.gritter
import random

import fedoratagger as ft
from fedoratagger.lib import model as m
from fedoratagger.frontend.widgets.voting import TagWidget, voting_js

rating_js = tw2.core.JSLink(
    link='rating/jquery.rating.js',
    resources=[tw2.jquery.jquery_js],
)
rating_dir = tw2.core.DirLink(filename='static/rating')
rating_css = tw2.core.CSSLink(
    link='rating/jquery.rating.css',
    resources=[rating_dir],
)

class CardWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    N = tw2.core.Param("Number of tags to show", default=5)
    package = tw2.core.Param(default=None)
    session = tw2.core.Param(default=None)
    tags = tw2.core.params.Variable()
    css_class = 'card'
    rating = None
    resources = [
        voting_js,
        rating_js,
        rating_css,
    ] + tw2.jqplugins.gritter.gritter_resources

    template = 'fedoratagger.frontend.widgets.templates.card'

    @property
    def not_anonymous(self):
        return flask.g.fas_user and not flask.g.fas_user.anonymous

    def prepare(self):
        super(CardWidget, self).prepare()

        if not self.package:
            self.package = m.Package.random(ft.SESSION)

        allowed_tags = filter(lambda t: not t.banned, self.package.tags)

        if len(allowed_tags) >= self.N:
            picked_tags = random.sample(allowed_tags, self.N)
        else:
            picked_tags = allowed_tags

        self.tags = [TagWidget(tag=tag) for tag in picked_tags]
        if self.tags:
            self.tags[0].css_class += " selected"

    def rating_selected(self, i, N):
        if self.rating is None:
            self.rating = self.package.rating(ft.SESSION) or 50
            if self.rating:
                self.rating = self.rating - 1

        target = int(float(self.rating) / 100.0 * N % (N))
        result = i == target and " selected" or ""
        return result

    @property
    def including_you(self):
        return flask.g.fas_user.uses(ft.SESSION, self.package)
