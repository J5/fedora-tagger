# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context
from tg.render import render
from tg import request
from tg.i18n import ugettext as _, ungettext
import fedoratagger.model as model
import fedoratagger.widgets.dialog
import fedoratagger.widgets.user

import tw2.core as twc
import tw2.jquery

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

        if 'login' not in environ['PATH_INFO']:
            for link in ["query.js", "cards.js", "navigation.js"]:
                twc.JSLink(link="javascript/%s" % link).req().prepare()

            tmpl_context.hotkeys_dialog = fedoratagger.widgets.dialog.HotkeysDialog
            tmpl_context.search_dialog = fedoratagger.widgets.dialog.SearchDialog
            tmpl_context.add_dialog = fedoratagger.widgets.dialog.AddTagDialog
            tmpl_context.user_widget = fedoratagger.widgets.user.UserWidget

        return TGController.__call__(self, environ, start_response)
