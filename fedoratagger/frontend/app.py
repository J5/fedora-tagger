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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA
#
# Refer to the README.rst and LICENSE files for full details of the license
# -*- coding: utf-8 -*-
"""The flask frontend app"""

import flask

from flask.ext.mako import render_template

import tw2.core
import tw2.jquery
import tw2.jqplugins.ui

import fedoratagger as ft
import fedoratagger.lib
from fedoratagger.lib import model as m
from fedoratagger.frontend.widgets.card import CardWidget
from fedoratagger.frontend.widgets.user import UserWidget
from fedoratagger.frontend.widgets.dialog import (
    HotkeysDialog,
    SearchDialog,
    LeaderboardDialog,
    StatisticsDialog,
    AddTagDialog,
)


FRONTEND = flask.Blueprint(
    'frontend', __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
    static_url_path='',
)

# Some template strings for the 'details' view.
icon_template = "images/favicons/16_{serv}.png"
item_template = "<li><img src='{icon}'/>" + \
    "<a href='{url}' target='_blank'>{text}</a></li>"
services = [
    ('beefy', 'Community', "/packages/{name}"),
    ('pkgdb', 'PackageDB', "https://admin.fedoraproject.org/pkgdb/package/"
        "{name}"),
    ('koji', 'Builds', "http://koji.fedoraproject.org/koji/search" +
        "?terms={name}&type=package&match=exact"),
    ('bodhi', 'Updates', "https://admin.fedoraproject.org/updates/{name}"),
    ('bugs', 'Bugs', "/packages/{name}/bugs"),
    ('sources', 'Source', "http://pkgs.fedoraproject.org/gitweb/" +
        "?p={name}.git"),
]


@FRONTEND.before_request
def before_request(*args, **kw):
    """ Function called for each request performed.
    It configures and injects globally required resources.
    """

    # Include jquery on every page.
    tw2.jquery.jquery_js.req().prepare()

    # Set the theme to 'hot-sneaks'
    tw2.jqplugins.ui.set_ui_theme_name('hot-sneaks')

    for link in ["utilities.js", "cards.js", "navigation.js"]:
        tw2.core.JSLink(link="javascript/%s" % link).req().prepare()

    flask.g.config = ft.APP.config

    flask.g.hotkeys_dialog = HotkeysDialog
    flask.g.search_dialog = SearchDialog
    flask.g.leaderboard_dialog = LeaderboardDialog
    flask.g.statistics_dialog = StatisticsDialog
    flask.g.user_widget = UserWidget

    flask.g.fas_user = fedoratagger.flask_utils.current_user(flask.request)

    if flask.g.fas_user and not flask.g.fas_user.anonymous:
        flask.g.add_dialog = AddTagDialog


@FRONTEND.route('/_heartbeat')
def heartbeat():
    """Fast heartbeat monitor so haproxy knows if we are runnining"""
    return "Lub-Dub"


# TODO -- determine wtf this is used for.. :/
@FRONTEND.route('/raw/<name>')
def raw(name):
    package = m.Package.by_name(ft.SESSION, name)

    html = "<html><body>"
    html += "<h1>" + package.name + "</h1>"
    html += "<h3>Tags/Votes/Voters</h3>"
    html += "<ul>"

    for tag in package.tags:
        html += "<li>"
        html += tag.label + "  " + str(tag.like - tag.dislike)
        html += "<ul>"
        for vote in tag.votes:
            html += "<li>" + vote.user.username + "</li>"
        html += "</ul>"
        html += "</li>"

    html += "</ul>"
    html += "</body></html>"
    return html


@FRONTEND.route('/card', defaults=dict(name=None))
@FRONTEND.route('/card/<name>')
def card(name):
    """ Handles the /card path.  Return a rendered CardWidget in HTML.

    If no name is specified, produce a widget for a package selected at
    random.

    If a name is specified, try to search for that package and render the
    associated CardWidget.
    """

    package = None
    if name and name != "undefined":
        package = m.Package.by_name(ft.SESSION, name)
    else:
        package = m.Package.random(ft.SESSION)

    w = CardWidget(package=package, session=ft.SESSION)
    return w.display()


@FRONTEND.route('/details', defaults=dict(name=None))
@FRONTEND.route('/details/<name>')
def details(name):
    """ Handles the /details path.

    Return a list of details for a package.
    """
    name = name or flask.request.args.get('name', None)

    items = [
        item_template.format(
            icon=icon_template.format(serv=serv),
            url=url.format(name=name),
            text=text
        ) for serv, text, url in services
    ]
    return "<ul>" + "\n".join(items) + "</ul>"


@FRONTEND.route('/leaderboard', defaults=dict(N=10))
@FRONTEND.route('/leaderboard/<int:N>')
def leaderboard(N):
    """ Handles the /leaderboard path.

    Returns an HTML table of the top N users.
    """

    # TODO -- 'N' is unused here.  need to dig a tunnel through the .lib api
    users = fedoratagger.lib.leaderboard(ft.SESSION)

    if N > len(users):
        N = len(users)

    keys = ['gravatar', 'name', 'score']
    row = "<tr>" + ''.join(["<td>{%s}</td>" % k for k in keys]) + "</tr>"
    rows = [
        row.format(**users[i + 1]) for i in range(N)
    ]
    template = """
    <table class="leaderboard">
    <tr>
        <th colspan="2">User</th>
        <th>Score</th>
    </tr>
    {rows}
    </table>"""
    return template.format(rows="".join(rows))


@FRONTEND.route('/', defaults=dict(name=None))
@FRONTEND.route('/<name>')
def home(name=None):
    """ Really, the main index.

    Returns a list of (the first three) card widgets for the
    template to render.  The rest are acquired as needed via ajax calls to
    the /card path.

    """

    if not name:
        name = m.Package.random(ft.SESSION).name
        flask.redirect(name)

    packages = [None] * 4

    if name:
        try:
            packages[1] = m.Package.by_name(ft.SESSION, name)
        except m.NoResultFound:
            packages[1] = m.Package()

    cards = [
        CardWidget(package=packages[i], session=ft.SESSION)
        for i in range(4)
    ]
    cards[1].css_class = 'card center'

    return render_template('tagger.mak', cards=cards,
                           title=cards[1].package.name)

@FRONTEND.route('/<name>/')
def home2(name=None):
    return flask.redirect(flask.request.url[:-1])

@FRONTEND.route('/login/', methods=('GET', 'POST'))
def auth_login():
    """ Method to log into the application. """
    next_url = flask.request.args.get('next', flask.url_for('frontend.home'))
    # If user is already logged in, return them to where they were last
    if flask.g.fas_user and not flask.g.fas_user.anonymous:
        return flask.redirect(next_url)
    return ft.FAS.login(return_url=next_url)


@FRONTEND.route('/logout/', methods=('GET', 'POST'))
def auth_logout():
    """ Method to log out of the application. """
    next_url = flask.request.args.get('next', flask.url_for('frontend.home'))
    # If user is already logged out, return them to where they were last
    if not flask.g.fas_user or flask.g.fas_user.anonymous:
        return flask.redirect(next_url)

    ft.FAS.logout()
    return flask.redirect(next_url)


@FRONTEND.route('/notifs_toggle/', methods=('GET', 'PATCH'))
def notifs_toggle():
    flask.g.fas_user.notifications_on = not flask.g.fas_user.notifications_on
    ft.SESSION.commit()

    jsonout = flask.jsonify(dict(
        notifications_on=flask.g.fas_user.notifications_on
    ))
    jsonout.status_code = 200

    return jsonout


#pulls out notification state without changing it
@FRONTEND.route('/notifs_state/', methods=('GET',))
def notifs_state():

    jsonout = flask.jsonify(dict(
        notifications_on=flask.g.fas_user.notifications_on
    ))
    jsonout.status_code = 200

    return jsonout
