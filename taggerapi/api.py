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
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import flask
from flask_fas_openid import FAS, fas_login_required
from functools import wraps

from taggerapi import APP, SESSION, FAS

import taggerlib
import forms as forms
import taggerlib.model as model


API = flask.Blueprint('api', __name__, url_prefix = '/api')


def pkg_get(pkgname):
    """ Performs the GET request of pkg. """
    httpcode = 200
    output = {}
    try:
        package = model.Package.by_name(SESSION, pkgname)
        output = package.__json__(SESSION)
    except SQLAlchemyError, err:
        SESSION.rollback()
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
        package = model.Package.by_name(SESSION, pkgname)
        output = package.__tag_json__()
    except SQLAlchemyError, err:
        SESSION.rollback()
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
        package = model.Package.by_name(SESSION, pkgname)
        output = package.__rating_json__(SESSION)
    except SQLAlchemyError, err:
        SESSION.rollback()
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
        package = model.Tag.by_label(SESSION, tag)
        if not package:
            raise SQLAlchemyError()
        output = {'tag': tag}
        output['packages'] = [pkg.__pkg_json__() for pkg in package]
    except SQLAlchemyError, err:
        SESSION.rollback()
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
                    messages.append(taggerlib.add_tag(SESSION, pkgname,
                                    item, flask.g.fas_user))
            SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = messages
        except NoResultFound, err:
            SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'Package "%s" not found' % pkgname
            httpcode = 404
        except SQLAlchemyError, err:
            SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'This tag is already associated to this package'
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


def rating_pkg_get(rating):
    """ Performs the GET request of rating pkg.
    Returns the list of packages having this rating.
    """
    httpcode = 200
    output = {}
    try:
        rating = float(rating)
        rates = model.Rating.by_rating(SESSION, rating)
        if not rates:
            raise SQLAlchemyError()
        output = {'rating': rating}
        output['packages'] = [rate.packages.name for rate in rates]
    except ValueError, err:
        SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = 'Invalid rating provided "%s"' % rating
        httpcode = 500
    except SQLAlchemyError, err:
        print err
        SESSION.rollback()
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
            message = taggerlib.add_rating(SESSION, pkgname, rating,
                                          flask.g.fas_user)
            SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = [message]
        except NoResultFound, err:
            SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'Package "%s" not found' % pkgname
            httpcode = 404
        except SQLAlchemyError, err:
            SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = 'You have already rated this package'
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
            message = taggerlib.add_vote(SESSION, pkgname, tag, vote,
                                        flask.g.fas_user)
            SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = [message]
        except taggerlib.TaggerapiException, err:
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


## Flask application


@API.before_request
def before_request(*args, **kw):
    """ Function called for each requests performed.
    Basically, it creates a user in the database using the information
    provided in the 'Authorization' header if provided, otherwise it
    uses the IP of the user.
    """
    token = None
    username = None
    authenticated = False
    if 'Authorization' in flask.request.headers:
        base64string = flask.request.headers['Authorization']
        base64string = base64string.split()[1].strip()
        userstring = base64.b64decode(base64string)
        (username, token) = userstring.split(':')
        user = model.FASUser.by_name(SESSION, username)
        if user \
            and user.api_token == token \
            and user.api_date >= datetime.date.today():
            authenticated = True
            flask.g.fas_user = user
    elif flask.request.remote_addr:
        user = model.FASUser.get_or_create(SESSION,
                                           flask.request.remote_addr)
        flask.g.fas_user = user
        authenticated = True
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
    return FAS.login(return_url=next_url)


@API.route('/token/')
@fas_login_required
def generate_token():
    """ Return the score of the specified user.
    """
    user = flask.g.fas_user
    output = taggerlib.get_api_token(SESSION, user)

    SESSION.commit()
    jsonout = flask.jsonify(output)
    return jsonout


@API.route('/random/')
def pkg_random():
    """ Returns a random package from the database.
    """
    httpcode = 200
    output = {}

    package = model.Package.random(SESSION)
    if not package:
        httpcode = 404
        output['output'] = 'notok'
        output['error'] = 'No package could be found'
    else:
        output = package.__json__(SESSION)

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


@API.route('/<pkgname>/rating/')
def pkg_rating(pkgname):
    """ Returns all known information about a package including it's
    icon, it's rating, it's tags...
    """
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
    for package in model.Package.all(SESSION):
        tmp = []
        for tag in package.tags:
            if tag.label.strip():
                tmp.append('%s\t%s' % (package.name, tag.label.strip()))
        if tmp:
            output.append('\n'.join(tmp))
    return flask.Response('\n'.join(output), mimetype='text/plain')


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
    """
    output = []
    for (ratingobj, rating) in model.Rating.all(SESSION):
        output.append('%s\t%s' % (ratingobj.packages.name,
                      rating))
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
    output = taggerlib.statistics(SESSION)
    jsonout = flask.jsonify(output)
    return jsonout


@API.route('/leaderboard/')
def leaderboard():
    """ Return the top 10 user, aka the leaderboard
    """
    output = taggerlib.leaderboard(SESSION)
    jsonout = flask.jsonify(output)
    return jsonout


@API.route('/score/<username>/')
def score(username):
    """ Return the score of the specified user.
    """
    httpcode = 200
    output = {}

    try:
        output = taggerlib.score(SESSION, username)
    except NoResultFound, err:
        httpcode = 404
        output['output'] = 'notok'
        output['error'] = 'User not found'

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout
