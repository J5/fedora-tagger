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
import tw2.jqplugins.gritter
import random

import fedoratagger as ft
from fedoratagger.lib import model as m
from fedoratagger.frontend.widgets.voting import TagWidget, voting_js


class CardWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    N = tw2.core.Param("Number of tags to show", default=5)
    package = tw2.core.Param(default=None)
    tags = tw2.core.params.Variable()
    css_class = 'card'
    resources = [voting_js] + tw2.jqplugins.gritter.gritter_resources

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
