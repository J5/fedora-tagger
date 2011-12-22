# -*- coding: utf-8 -*-
"""Main Controller"""

import random

from tg import expose, flash, require, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from paste.deploy.converters import asbool
from repoze.what.predicates import not_anonymous

from fedoratagger import model
from fedoratagger.model import DBSession, metadata

from fedoratagger.lib.base import BaseController
from fedoratagger.controllers.error import ErrorController

from fedoratagger.widgets.card import CardWidget

from fedoratagger.lib.utils import dump2json

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the fedora-tagger application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    error = ErrorController()

    @expose('fedoratagger.templates.index')
    def index(self):
        """Handle the front-page."""
        redirect(url('/tagger'))

    @expose('json')
    def dump(self):
        return dump2json()

    def _search_query(self, term):
        query = model.Package.query.filter_by(name=term)

        if query.count() != 1:
            # Broaden the search
            query = model.Package.query.filter(
                model.Package.name.like("%%%s%%" % term))

        return query

    @expose('json')
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def search(self, term):
        query = self._search_query(term)

        return dict(
            count=query.count(),
            term=term,
            samples=[p.name for p in query.all()[:3]]
        )

    @expose('json')
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def add(self, label, package):
        json = dict(tag=label, package=package)

        query = model.TagLabel.query.filter_by(label=label)
        if query.count() == 0:
            model.DBSession.add(model.TagLabel(label=label))

        label = query.one()

        query = model.Package.query.filter_by(name=package)
        if query.count() == 0:
            json['msg'] = "No such package '%s'" % package
            return json

        package = query.one()

        query = model.Tag.query.filter_by(label=label, package=package)

        if query.count() != 0:
            json['msg'] = "%s already tagged '%s'" % (package.name, label.label)
            return json

        tag = model.Tag(label=label, package=package)
        model.DBSession.add(tag)

        vote = model.Vote(like=True)
        vote.user = model.get_user()
        vote.tag = tag
        model.DBSession.add(vote)

        json['msg'] = "Success.  '%s' added to package '%s'" % (
            label.label, package.name)
        return json


    @expose('fedoratagger.templates.tagger')
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def tagger(self):
        packages = model.Package.query.all()
        n = len(packages)
        cards = [CardWidget(package=p) for p in random.sample(packages, 3)]
        cards[1].css_class = 'card center'
        return dict(cards=cards)

    @expose()
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def card(self, name=None):
        if name and name != "undefined":
            query = self._search_query(name)
            package = query.first()
        else:
            packages = model.Package.query.all()
            package = random.sample(packages, 1)[0]

        w = CardWidget(package=package)
        return w.display()

    @expose('json')
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def vote(self, id, like):
        like = asbool(like)
        tag = model.Tag.query.filter_by(id=id).one()
        user = model.get_user()

        # See if they've voted on this before.
        query = model.Vote.query.filter_by(user=user, tag=tag)
        if query.count() == 0:
            # They haven't.  So register a new vote.
            if like:
                tag.like += 1
            else:
                tag.dislike += 1

            vote = model.Vote(like=like)
            vote.user = user
            vote.tag = tag
            model.DBSession.add(vote)
        else:
            # Otherwise, they've voted on this before.  See if they're changing
            # their vote.
            vote = query.one()
            if vote.like == like:
                # They're casting the same vote, the same way.  Ignore them.
                pass
            else:
                # Okay.  Let them change their vote.
                if like:
                    tag.like += 1
                    tag.dislike -= 1
                else:
                    tag.like -= 1
                    tag.dislike += 1

                vote.like = like
                # Done changing vote.

        json = tag.__json__()
        json['user'] = {
            'votes': user.total_votes,
            'rank': user.rank,
        }
        return json

    @expose('fedoratagger.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
