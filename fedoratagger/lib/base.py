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
# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context
from tg.render import render
from tg import request
from pylons.i18n import ugettext as _, ungettext
import fedoratagger.model as model

from fedoratagger.widgets.user import UserWidget
from fedoratagger.widgets.dialog import (
    HotkeysDialog,
    SearchDialog,
    LeaderboardDialog,
    StatisticsDialog,
    AddTagDialog,
)

import tw2.core as twc
import tw2.jquery
import tw2.jqplugins.ui

__all__ = ['BaseController']


class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity

        # Include jquery on every page.
        tw2.jquery.jquery_js.req().prepare()

        # Set the theme to 'hot-sneaks'
        tw2.jqplugins.ui.set_ui_theme_name('hot-sneaks')

        if 'login' not in environ['PATH_INFO']:
            for link in ["query.js", "cards.js", "navigation.js"]:
                twc.JSLink(link="javascript/%s" % link).req().prepare()

            tmpl_context.hotkeys_dialog = HotkeysDialog
            tmpl_context.search_dialog = SearchDialog
            tmpl_context.leaderboard_dialog = LeaderboardDialog
            tmpl_context.statistics_dialog = StatisticsDialog
            tmpl_context.user_widget = UserWidget
            if request.identity:
                tmpl_context.add_dialog = AddTagDialog

        return TGController.__call__(self, environ, start_response)
