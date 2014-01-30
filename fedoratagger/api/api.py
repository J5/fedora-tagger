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
"""The flask API application"""

import base64
import datetime
from urlparse import urljoin, urlparse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import flask
from functools import wraps

import fedoratagger as ft

import fedoratagger.lib
import fedoratagger.lib.model as model
import fedoratagger.flask_utils

# Relative import
import forms as forms


API = flask.Blueprint(
    'api', __name__,
    url_prefix='/api/v1',
    template_folder='templates',
    static_folder='static',
)


def pkg_get(pkgname):
    """ Performs the GET request of pkg. """
    httpcode = 200
    output = {}
    try:
        package = model.Package.by_name(ft.SESSION, pkgname)
        output = package.__json__(ft.SESSION)
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Package "%s" not found' % pkgname
        httpcode = 404

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def pkg_get_tag(pkgname):
    """ Performs the GET request of pkg_tag. """
    httpcode = 200
    output = {}
    try:
        package = model.Package.by_name(ft.SESSION, pkgname)
        output = package.__tag_json__()
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Package "%s" not found' % pkgname
        httpcode = 404

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def pkg_get_usage(pkgname):
    """ Performs the GET request of pkg_usage. """
    httpcode = 200
    output = {}
    try:
        if isinstance(pkgname, list):
            tmp = []
            for pkg in pkgname:
                package = model.Package.by_name(ft.SESSION, pkg)
                tmp.append(package.__usage_json__(ft.SESSION))
            output['usage'] = tmp
        else:
            package = model.Package.by_name(ft.SESSION, pkgname)
            output = package.__usage_json__(ft.SESSION)
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Package "%s" not found' % pkgname
        httpcode = 404

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def pkg_get_rating(pkgname):
    """ Performs the GET request of pkg_rating. """
    httpcode = 200
    output = {}
    try:
        if isinstance(pkgname, list):
            tmp = []
            for pkg in pkgname:
                package = model.Package.by_name(ft.SESSION, pkg)
                tmp.append(package.__rating_json__(ft.SESSION))
            output['ratings'] = tmp
        else:
            package = model.Package.by_name(ft.SESSION, pkgname)
            output = package.__rating_json__(ft.SESSION)
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Package "%s" not found' % pkgname
        httpcode = 404

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def tag_pkg_get(tag):
    """ Performs the GET request of tag_pkg.
    Returns all the package associated to this tag.
    """
    httpcode = 200
    output = {}
    try:
        package = model.Tag.by_label(ft.SESSION, tag)
        if not package:
            raise NoResultFound()
        output = {'tag': tag}
        output['packages'] = [pkg.__pkg_json__() for pkg in package]
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Tag "%s" not found' % tag
        httpcode = 404

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def tag_pkg_put(pkgname):
    """ Performs the PUT request of tag_pkg. """
    httpcode = 200
    output = {}
    form = forms.AddTagForm(csrf_enabled=False)
    if form.validate_on_submit():
        pkgname = form.pkgname.data
        tag = form.tag.data
        try:
            if ',' in tag:
                tag = tag.split(',')
            else:
                tag = [tag]
            messages = []
            for item in tag:
                item = item.strip()
                if item:
                    messages.append(fedoratagger.lib.add_tag(ft.SESSION, pkgname,
                                    item, flask.g.fas_user))
            ft.SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = messages
            output['user'] = flask.g.fas_user.__json__()
        except NoResultFound, err:
            ft.SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'Package "%s" not found' % pkgname
            httpcode = 404
        except IntegrityError, err:
            ft.SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'This tag is already associated to this package'
            httpcode = 500
        except ValueError, err:
            ft.SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = str(err)
            httpcode = 406
    else:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        if form.errors:
            detail = []
            for error in form.errors:
                detail.append('%s: %s' % (error,
                              '; '.join(form.errors[error])))
            output['error_detail'] = detail
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def rating_pkg_get(rating):
    """ Performs the GET request of rating pkg.
    Returns the list of packages having this rating.
    """
    httpcode = 200
    output = {}
    try:
        rating = float(rating)
        packages = model.Rating.by_rating(ft.SESSION, rating)
        if not packages:
            raise NoResultFound()
        output = {'rating': rating}
        output['packages'] = [package.name for package in packages]
    except ValueError, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Invalid rating provided "%s"' % rating
        httpcode = 500
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'No packages found with rating "%s"' % rating
        httpcode = 404

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def rating_pkg_put(pkgname):
    """ Performs the PUT request of rating_pkg. """
    httpcode = 200
    output = {}
    form = forms.AddRatingForm(csrf_enabled=False)
    if form.validate_on_submit():
        pkgname = form.pkgname.data
        rating = form.rating.data
        try:
            message = fedoratagger.lib.add_rating(ft.SESSION, pkgname, rating,
                                                  flask.g.fas_user)
            ft.SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = [message]
            output['user'] = flask.g.fas_user.__json__()
        except NoResultFound, err:
            ft.SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'Package "%s" not found' % pkgname
            httpcode = 404

    else:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        if form.errors:
            detail = []
            for error in form.errors:
                detail.append('%s: %s' % (error,
                              '; '.join(form.errors[error])))
            output['error_detail'] = detail
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def usage_pkg_get(pkgname):
    """ Performs the GET request of usage_pkg. """
    user = model.FASUser.by_name(ft.SESSION, flask.g.fas_user.username)
    output = dict(
        user=user.__json__(ft.SESSION),
        pkgname=pkgname,
        usage=False,
    )

    for usage in user.usages:
        if pkgname == usage.package.name:
            output['usage'] = True

    jsonout = flask.jsonify(output)
    jsonout.status_code = 200
    return jsonout


def usage_pkg_put(pkgname):
    """ Performs the PUT request of usage_pkg. """
    httpcode = 200
    output = {}
    form = forms.SetUsageForm(csrf_enabled=False)
    if form.validate_on_submit():
        pkgname = form.pkgname.data
        usage =  form.usage.data

        # Not sure how to do this with just wtforms.
        # The BooleanField didn't behave like I want.
        if usage == 'true':
            usage = True
        elif usage == 'false':
            usage = False
        else:
            output['output'] = 'notok'
            output['error'] = 'Invalid input submitted'
            output['error_detail'] = 'usage must be "true" or "false"'
            httpcode = 500
            jsonout = flask.jsonify(output)
            jsonout.status_code = httpcode
            return jsonout

        try:
            message = fedoratagger.lib.set_usage(
                ft.SESSION, pkgname, flask.g.fas_user, usage)
            ft.SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = [message]
            output['user'] = flask.g.fas_user.__json__()
        except NoResultFound, err:
            ft.SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'Package "%s" not found' % pkgname
            httpcode = 404

    else:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        if form.errors:
            detail = []
            for error in form.errors:
                detail.append('%s: %s' % (error,
                              '; '.join(form.errors[error])))
            output['error_detail'] = detail
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def vote_pkg_put(pkgname):
    """ Performs the PUT request of vote_tag_pkg. """
    httpcode = 200
    output = {}
    form = forms.VoteTagForm(csrf_enabled=False)
    if form.validate_on_submit():
        pkgname = form.pkgname.data
        tag = form.tag.data
        vote = int(form.vote.data) == 1
        try:
            message = fedoratagger.lib.add_vote(ft.SESSION, pkgname, tag, vote,
                                                flask.g.fas_user)
            ft.SESSION.commit()

            package = model.Package.by_name(ft.SESSION, pkgname)
            tagobj = model.Tag.get(ft.SESSION, package.id, tag)

            output['output'] = 'ok'
            output['messages'] = [message]
            output['user'] = flask.g.fas_user.__json__()
            output['tag'] = tagobj.__json__()
        except fedoratagger.lib.TaggerapiException, err:
            output['output'] = 'notok'
            output['error'] = err.message
            httpcode = 500
    else:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        if form.errors:
            detail = []
            for error in form.errors:
                detail.append('%s: %s' % (error,
                              '; '.join(form.errors[error])))
            output['error_detail'] = detail
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def statistics_by_user_get(username, fields="all"):
    """
    Get statistics per user from username (if exist)
    """
    httpcode = 200
    try:
        user = model.FASUser.by_name(ft.SESSION, username)
        output = fedoratagger.lib.statistics_by_user(ft.SESSION,
                                                     user, fields)
    except NoResultFound, err:
        ft.SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'User "%s" not found' % username
        httpcode = 404
    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def fas_login_required(function):
    """ Flask decorator to ensure that the user is logged in against FAS.
    To use this decorator you need to have a function named 'auth_login'.
    Without that function the redirect if the user is not logged in will not
    work.
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if flask.g.fas_user is None:
            return flask.redirect(flask.url_for('api.auth_login',
                                                next=flask.request.url))
        return function(*args, **kwargs)
    return decorated_function


## Flask application


@API.before_request
def before_request(*args, **kw):
    """ Function called for each requests performed.
    Basically, it creates a user in the database using the information
    provided in the 'Authorization' header if provided, otherwise it
    uses the IP of the user.
    """
    # We only care about PUT request actually...
    if flask.request.method != 'PUT':
        return

    flask.g.fas_user = fedoratagger.flask_utils.current_user(flask.request)
    # XXX - the user can be 'authenticated' but still be 'anonymous'.  Odd.
    authenticated = bool(flask.g.fas_user)

    # if we don't check that we're requesting /loging/ we can't (log in)
    if not authenticated and flask.request.path != '/api/login/':
        output = {'output': 'notok', 'error': 'Login invalid/expired'}
        jsonout = flask.jsonify(output)
        jsonout.status_code = 500
        return jsonout


@API.route('/')
def index():
    """ Displays the information page on how to use the API.
    """
    return flask.render_template('api.html')


@API.route('/login/', methods=('GET', 'POST'))
def auth_login():
    """ Method to log into the application. """
    next_url = flask.request.args.get('next', flask.url_for('api.index'))
    # If user is already logged in, return them to where they were last
    if flask.g.fas_user:
        return flask.redirect(next_url)
    return ft.FAS.login(return_url=next_url)


@API.route('/token/')
@fas_login_required
def generate_token():
    """ Return the score of the specified user.
    """
    user = flask.g.fas_user
    output = fedoratagger.lib.get_api_token(ft.SESSION, user)

    ft.SESSION.commit()
    jsonout = flask.jsonify(output)
    return jsonout


@API.route('/random/')
def pkg_random():
    """ Returns a random package from the database.
    """
    httpcode = 200
    output = {}

    try:
        package = model.Package.random(ft.SESSION)
        output = package.__json__(ft.SESSION)
    except NoResultFound:
        httpcode = 404
        output['output'] = 'notok'
        output['error'] = 'No package could be found'

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


@API.route('/<pkgname>/')
def pkg(pkgname):
    """ Returns all known information about a package including it's
    icon, it's rating, it's tags...
    """
    return pkg_get(pkgname)


@API.route('/<pkgname>/tag/')
def pkg_tag(pkgname):
    """ Returns all known information about a package including it's
    icon, it's rating, it's tags...
    """
    return pkg_get_tag(pkgname)


@API.route('/<pkgname>/usage/')
def pkg_usage(pkgname):
    """ Returns all known information about a package including it's
    icon, it's usage, it's tags...
    """
    return pkg_get_usage(pkgname)


@API.route('/<pkgname>/rating/')
def pkg_rating(pkgname):
    """ Returns all known information about a package including it's
    icon, it's rating, it's tags...
    """
    return pkg_get_rating(pkgname)


@API.route('/ratings/<pkgname>/', methods=['GET'])
def pkg_ratings(pkgname):
    """ Returns the ratings associated with several packages
    """
    if ',' in pkgname:
        pkgname = pkgname.split(',')

    return pkg_get_rating(pkgname)


@API.route('/tag/<pkgname>/', methods=['GET', 'PUT'])
def tag_pkg(pkgname):
    """ Returns the tags associated with a package
    """
    if flask.request.method == 'GET':
        return tag_pkg_get(pkgname)
    elif flask.request.method == 'PUT':
        return tag_pkg_put(pkgname)


@API.route('/tag/dump/')
def tag_pkg_dump():
    """ Returns a tab separated list of all tags for all packages
    """
    output = []
    for package in model.Package.all(ft.SESSION):
        tmp = []
        for tag in package.tags:
            if tag.label.strip():
                tmp.append('%s\t%s' % (package.name, tag.label.strip()))
        if tmp:
            output.append('\n'.join(tmp))
    return flask.Response('\n'.join(output), mimetype='text/plain')


@API.route('/tag/export/')
def tag_pkg_export():
    """ Returns a JSON blob of all tags for all packages.

    The format is a little funky, but it exists for backwards compatibility
    with the fedora-packages webapp.  It has a cronjob which scrapes this
    URL on the nightly.
    """

    output = dict(packages=[])
    for package in model.Package.all(ft.SESSION):
        tmp = {package.name: []}
        for tag in package.tags:
            if tag.label.strip():
                tmp[package.name].append({
                    'tag': tag.label.strip(),
                    'total': tag.total,
                })
        output['packages'].append(tmp)
    return flask.jsonify(output)


@API.route('/tag/sqlitebuildtags/')
def tag_pkg_sqlite():
    """ Returns a sqlite blob of all tags for all packages.

    This export format is consumed by the bodhi masher for inclusion
    in created yum repositories.
    """
    return fedoratagger.lib.sqlitebuildtags()


@API.route('/usage/<pkgname>/', methods=['GET', 'PUT'])
def usage_pkg(pkgname):
    """ Returns the usage associated with a package
    """
    if flask.request.method == 'GET':
        return usage_pkg_get(pkgname)
    elif flask.request.method == 'PUT':
        return usage_pkg_put(pkgname)


@API.route('/rating/<pkgname>/', methods=['GET', 'PUT'])
def rating_pkg(pkgname):
    """ Returns the rating associated with a package
    """
    if flask.request.method == 'GET':
        return rating_pkg_get(pkgname)
    elif flask.request.method == 'PUT':
        return rating_pkg_put(pkgname)


@API.route('/rating/dump/')
def rating_pkg_dump():
    """ Returns a tab separated list of the rating of each packages

    Format:
        NAME    RATING    NUMBER OF VOTES     NUMBER OF INSTALLS

    """
    output = []
    for (package, rating) in model.Rating.all(ft.SESSION):
        n_ratings = len(package.ratings)
        n_users = model.Usage.usage_of_package(ft.SESSION, package.id)
        output.append('%s\t%0.1f\t%i\t%i' % (
            package.name, rating, n_ratings, n_users))
    return flask.Response('\n'.join(output), mimetype='text/plain')


@API.route('/vote/<pkgname>/', methods=['PUT'])
def vote_tag_pkg(pkgname):
    """ Vote on a specific tag of a package
    """
    return vote_pkg_put(pkgname)


@API.route('/statistics/')
def statistics():
    """ Return the statistics of the package/tags in the database
    """
    output = fedoratagger.lib.statistics(ft.SESSION)
    jsonout = flask.jsonify(output)
    return jsonout


@API.route('/statistics-user/<username>/<fields>')
def statistics_by_user(username, fields="all"):
    """ Return the statistics of the user votes
    """
    return statistics_by_user_get(username, fields)


@API.route('/leaderboard/')
def leaderboard():
    """ Return the top 10 user, aka the leaderboard
    """
    output = fedoratagger.lib.leaderboard(ft.SESSION)
    jsonout = flask.jsonify(output)
    return jsonout


@API.route('/score/<username>/')
def score(username):
    """ Return the score of the specified user.
    """
    httpcode = 200
    output = {}

    try:
        output = fedoratagger.lib.score(ft.SESSION, username)
    except NoResultFound, err:
        httpcode = 404
        output['output'] = 'notok'
        output['error'] = 'User not found'

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout
