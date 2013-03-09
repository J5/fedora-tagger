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
"""The flask application"""

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources


import ConfigParser
import os
import datetime
from urlparse import urljoin, urlparse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import flask

import taggerlib
import forms as forms
import taggerlib.model as model

# Create the application.
APP = flask.Flask(__name__)
# set up FAS
APP.config.from_object('taggerapi.default_config')
if 'TAGGERAPI_CONFIG' in os.environ:  # pragma: no cover
    APP.config.from_envvar('TAGGERAPI_CONFIG')
SESSION = taggerlib.create_session(APP.config['DB_URL'])


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


def tag_pkg_get(pkgname):
    """ Performs the GET request of tag_pkg. """
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
            ipaddress = flask.request.remote_addr
            for item in tag:
                item = item.strip()
                if item:
                    messages.append(taggerlib.add_tag(SESSION, pkgname,
                                    item, ipaddress))
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


def rating_pkg_get(pkgname):
    """ Performs the GET request of rating_pkg. """
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


def rating_pkg_put(pkgname):
    """ Performs the PUT request of rating_pkg. """
    httpcode = 200
    output = {}
    form = forms.AddRatingForm(csrf_enabled=False)
    if form.validate_on_submit():
        pkgname = form.pkgname.data
        rating = form.rating.data
        try:
            message= taggerlib.add_rating(SESSION, pkgname, rating,
                                          flask.request.remote_addr)
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
            message= taggerlib.add_vote(SESSION, pkgname, tag, vote,
                                        flask.request.remote_addr)
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


@APP.route('/')
def index():
    """ Displays the information page on how to use the API.
    """
    return flask.render_template('api.html')


@APP.route('/<pkgname>/')
def pkg(pkgname):
    """ Returns all known information about a package including it's
    icon, it's rating, it's tags...
    """
    return pkg_get(pkgname)


@APP.route('/tag/<pkgname>/', methods=['GET', 'PUT'])
def tag_pkg(pkgname):
    """ Returns the tags associated with a package
    """
    if flask.request.method == 'GET':
        return tag_pkg_get(pkgname)
    elif flask.request.method == 'PUT':
        return tag_pkg_put(pkgname)


@APP.route('/tag/dump/')
def tag_pkg_dump():
    """ Returns a tab separated list of all tags for all packages
    """
    output = []
    for package in model.Package.all(SESSION):
        tmp = []
        for tag in package.tags:
            tmp.append('%s\t%s' % (package.name, tag.label))
        output.append('\n'.join(tmp))
    return flask.Response('\n'.join(output), mimetype='text/plain')


@APP.route('/rating/<pkgname>/', methods=['GET', 'PUT'])
def rating_pkg(pkgname):
    """ Returns the rating associated with a package
    """
    if flask.request.method == 'GET':
        return rating_pkg_get(pkgname)
    elif flask.request.method == 'PUT':
        return rating_pkg_put(pkgname)


@APP.route('/rating/dump/')
def rating_pkg_dump():
    """ Returns a tab separated list of the rating of each packages
    """
    output = []
    for (ratingobj, rating) in model.Rating.all(SESSION):
        output.append('%s\t%s' % (ratingobj.package.name,
                      rating))
    return flask.Response('\n'.join(output), mimetype='text/plain')


@APP.route('/vote/<pkgname>/', methods=['PUT'])
def vote_tag_pkg(pkgname):
    """ Vote on a specific tag of a package
    """
    return vote_pkg_put(pkgname)


if __name__ == '__main__':  # pragma: no cover
    import sys
    sys.path.insert(0, '..')
    APP.debug = True
    APP.run()
