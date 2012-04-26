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
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from tg import session
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from paste.deploy.converters import asbool
from repoze.what.predicates import not_anonymous

import re
import os
from sqlalchemy import func

from fedoratagger import model
from fedoratagger.model import DBSession, metadata

from fedoratagger.lib.base import BaseController
from fedoratagger.controllers.error import ErrorController

from fedoratagger.widgets.card import CardWidget

from fedoratagger.lib.utils import dump2json

__all__ = ['RootController']


def load_dirty_words():
    sep = os.path.sep
    fname = sep.join(__file__.split(sep)[:-2]) + "/dirtywords.txt"
    with open(fname) as f:
        return [line.strip() for line in f.readlines()]

dirty_words = load_dirty_words()

pattern = re.compile('[^\w^\s^-^\.^#^+]+', re.UNICODE)

class RootController(BaseController):
    """ The root controller for the fedora-tagger application. """

    error = ErrorController()

    @expose()
    def _heartbeat(self, *args, **kwds):
        """Fast heartbeat monitor so proxy servers know if we are runnining"""
        # TODO: perhaps we want to monitor our own internal functions and
        #       send back an error if we are not completely up and running
        return "Still running"

    @expose()
    def _update(self):
        import fedoratagger.websetup.bootstrap
        # This could take a long time
        fedoratagger.websetup.bootstrap.import_pkgdb_tags()

    @expose('json')
    def dump(self):
        """ A http interface to the dump2json method.

        Returns a json dump of the database (nearly) in full.
        """
        return dump2json()

    def _search_query(self, term):
        """ Produce a query searching over packages for ``term`` """

        query = model.Package.query.filter_by(name=term)

        if query.count() != 1:
            # Broaden the search
            query = model.Package.query.filter(
                model.Package.name.like("%%%s%%" % term))

        return query

    @expose()
    def raw(self, name):

        print name
        package = model.Package.query.filter_by(name=name).one()

        html = "<html><body>"
        html += "<h1>" + package.name + "</h1>"
        html += "<h3>Tags/Votes/Voters</h3>"
        html += "<ul>"

        for tag in package.tags:
            html += "<li>"
            html += tag.label.label + "  " + str(tag.total_votes)
            html += "<ul>"
            for vote in tag.votes:
                html += "<li>" + vote.user.username + "</li>"
            html += "</ul>"
            html += "</li>"

        html += "</ul>"
        html += "</body></html>"
        return html



    @expose('json')
    def search(self, term):
        """ Handles /search URL.

        Returns a JSON object including how many items were found, and a (few)
        samples.
        """


        query = self._search_query(term)

        return dict(
            count=query.count(),
            term=term,
            samples=[p.name for p in query.all()[:3]]
        )

    @expose('json')
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def add(self, labels, package):
        """ Handles /add URL.

        Returns a JSON object indicating success or failure.

         - If the package does not exist.  Fail.
         - If the label does not exist, create it.
         - If the label is not associated with the package, associate it.
         - Log a 'vote' for the current user on the new tag.

        """

        # Some scrubbing
        labels = [l.lower().strip() for l in labels.split(',')]
        labels = [pattern.sub('', label) for label in labels]
        # No empty strings
        labels = [label for label in labels if label]
        # Uniqify
        labels = list(set(labels))

        # Setup our return object
        json = dict(tags=", ".join(labels), package=package)
        json['tag'] = json['tags']

        if not labels:
            json['msg'] = "You may not use an empty label."
            return json

        if any([label in dirty_words for label in labels]):
            json['msg'] = "That's not nice."
            return json

        query = model.Package.query.filter_by(name=package)
        if query.count() == 0:
            json['msg'] = "No such package '%s'" % package
            return json

        package = query.one()

        for label in labels:
            query = model.TagLabel.query.filter_by(label=label)
            if query.count() == 0:
                model.DBSession.add(model.TagLabel(label=label))

            label = query.first()

            query = model.Tag.query.filter_by(label=label, package=package)

            if query.count() != 0:
                json['msg'] = "%s already tagged '%s'" % (
                    package.name, label.label)
                return json

            tag = model.Tag(label=label, package=package)
            model.DBSession.add(tag)

            vote = model.Vote(like=True)
            user = model.get_user()
            vote.user = user
            vote.tag = tag
            model.DBSession.add(vote)

        json['msg'] = "Success.  '%s' added to package '%s'" % (
            ', '.join(labels), package.name)
        json['user'] = {
            'votes': user.total_votes,
            'rank': user.rank,
        }
        return json

    @expose('json')
    @require(not_anonymous(msg="Login with your FAS credentials."))
    def notifs_toggle(self):
        """ Toggle the currently-logged-in-user's notifications setting """
        user = model.get_user()
        user.notifications_on = not user.notifications_on
        return dict(notifications_on=user.notifications_on)


    @expose('fedoratagger.templates.tagger')
    def tagger(self, name=None):
        """ Really, the main index.

        Returns a list of (the first three) card widgets for the
        template to render.  The rest are acquired as needed via ajax calls to
        the /card path.

        """

        if not name:
            name = model.Package.query.order_by(func.random()).first().name
            redirect(name)

        packages = [None] * 3

        if name:
            packages[1] = model.Package.query.filter_by(name=name).first()

        cards = [CardWidget(package=packages[i]) for i in range(3)]
        cards[1].css_class = 'card center'
        return dict(cards=cards)

    index = tagger
    default = tagger  # For old TG
    _default = tagger # For new TG

    @expose('json')
    @expose('fedoratagger.templates.statistics', content_type='text/html')
    def statistics(self):
        """ Handles the /statistics path.

        Returns an HTML table of statistics on tagged packages.
        """

        packages = model.Package.query.all()
        n_tags = model.TagLabel.query.count()
        raw_data = dict([(p.name, len(p.tags)) for p in packages])

        n_packs = len(raw_data)
        no_tags = len([v for v in raw_data.values() if not v])
        with_tags = n_packs - no_tags

        tags_per_package = sum([len(p.tags) for p in packages]) \
                / float(n_packs)
        tags_per_package_no_zeroes = sum([len(p.tags) for p in packages]) \
                / float(with_tags)

        return {
            'raw': raw_data,
            'summary': {
                'total_packages': n_packs,
                'total_unique_tags': n_tags,
                'no_tags': no_tags,
                'with_tags': with_tags,
                'tags_per_package': "%.2f" % tags_per_package,
                'tags_per_package_no_zeroes': "%.2f" % tags_per_package_no_zeroes,
            },
        }

    @expose()
    def leaderboard(self, N=10):
        """ Handles the /leaderboard path.

        Returns an HTML table of the top N users.
        """

        query = model.FASUser.query
        users = query.filter(model.FASUser.username!='anonymous').all()
        users.sort(lambda x, y: cmp(len(x.votes), len(y.votes)), reverse=True)
        users = users[:N]

        keys = ['rank', 'gravatar_sm', 'username', 'total_votes']
        row = "<tr>" + ''.join(["<td>{%s}</td>" % k for k in keys]) + "</tr>"
        rows = [
            row.format(**dict([(k, getattr(u, k)) for k in keys]))
            for u in users
        ]
        template = """
        <table class="leaderboard">
        <tr>
            <th>Rank</th>
            <th colspan="2">User</th>
            <th>Votes</th>
        </tr>
        {rows}
        </table>"""
        return template.format(rows="".join(rows))


    @expose()
    def details(self, name=None):
        """ Handles the /details path.

        Return a list of details for a package.
        """

        icon_template = "images/favicons/16_{serv}.png"
        item_template = "<li><img src='{icon}'/><a href='{url}' target='_blank'>{text}</a></li>"
        services = [
            ('beefy', 'Community', "https://community.dev.fedoraproject.org/packages/{name}"),
            ('pkgdb', 'Downloads', "https://admin.fedoraproject.org/community/?package={name}#package_maintenance/details/downloads"),
            ('koji', 'Builds', "http://koji.fedoraproject.org/koji/search?terms={name}&type=package&match=exact"),
            ('bodhi', 'Updates', "https://admin.fedoraproject.org/updates/{name}"),
            ('bugs', 'Bugs', "https://admin.fedoraproject.org/pkgdb/acls/bugs/{name}"),
            ('sources', 'Source', "http://pkgs.fedoraproject.org/gitweb/?p={name}.git"),
        ]

        items = [
            item_template.format(
                icon=icon_template.format(serv=serv),
                url=url.format(name=name),
                text=text
            ) for serv, text, url in services
        ]
        return "<ul>" + "\n".join(items) + "</ul>"


    @expose()
    def card(self, name=None):
        """ Handles the /card path.  Return a rendered CardWidget in HTML.

        If no name is specified, produce a widget for a package selected at
        random.

        If a name is specified, try to search for that package and render the
        associated CardWidget.

        """

        package = None
        if name and name != "undefined":
            query = self._search_query(name)
            package = query.first()

        w = CardWidget(package=package)
        return w.display()

    @expose('json')
    def vote(self, id, like):
        """ Handles the /vote path.  Return JSON indicating results and stats.

        If the user has voted on this tag before, only allow a 'change' of
        votes; no "double-voting".

        If they have not, then register their new vote.
        """

        like = asbool(like)
        tag = model.Tag.query.filter_by(id=id).one()
        user = model.get_user()

        if not user.anonymous:
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
        else:
            # They *are* anonymous.  Let them vote, but not twice this session.
            if tag not in session.get('tags_voted_on', []):
                session['tags_voted_on'] = session.get('tags_voted_on', []) + [tag]
                session.save()

                if like:
                    tag.like += 1
                else:
                    tag.dislike += 1

        # Delete really stupid tags
        if tag.total < -10:
            model.DBSession.delete(tag)

        json = tag.__json__()
        json['user'] = {
            'votes': user.total_votes,
            'rank': user.rank,
        }
        return json

    @expose('fedoratagger.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!' % userid))
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
