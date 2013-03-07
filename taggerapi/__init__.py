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
"""The flask application"""

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources


import ConfigParser
import os
import datetime
from urlparse import urljoin, urlparse
from sqlalchemy.exc import SQLAlchemyError

import flask

import taggerlib
import forms as forms
import taggerlib.model as model

# Create the application.
APP = flask.Flask(__name__)
# set up FAS
APP.config.from_object('taggerapi.default_config')
#APP.config.from_envvar('TAGGERAPI_CONFIG')
SESSION = taggerlib.create_session(APP.config['DB_URL'])


def get_tag_pkg(pkgname):
    """ Performs the GET request of tag_pkg. """
    httpcode = 200
    output = {}
    try:
        package = model.Package.by_name(SESSION, pkgname)
        output = package.__tag_json__()
    except SQLAlchemyError, err:
        SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = err.message
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def post_tag_pkg(pkgname):
    """ Performs the POST request of tag_pkg. """
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
                messages.append(taggerlib.add_tag(SESSION, pkgname, item))
            SESSION.commit()
            output['output'] = 'ok'
            output['messages'] = messages
        except taggerlib.TaggerapiException, err:
            output['output'] = 'notok'
            output['error'] = err.message
            httpcode = 500
        except SQLAlchemyError, err:
            SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = err.message
            httpcode = 500
    else:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        if form.errors:
            detail = []
            for error in form.errors:
                detail.append('%s: %s' % (error, '; '.join(form.errors[error])))
            output['error_detail'] = detail
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def get_rating_pkg(pkgname):
    """ Performs the GET request of rating_pkg. """
    httpcode = 200
    output = {}
    try:
        package = model.Package.by_name(SESSION, pkgname)
        output = package.__rating_json__(SESSION)
    except SQLAlchemyError, err:
        SESSION.rollback()
        output['output'] = 'notok'
        output['error'] = err.message
        httpcode = 500

    jsonout = flask.jsonify(output)
    jsonout.status_code = httpcode
    return jsonout


def post_rating_pkg(pkgname):
    """ Performs the POST request of rating_pkg. """
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
        except taggerlib.TaggerapiException, err:
            output['output'] = 'notok'
            output['error'] = err.message
            httpcode = 500
        except SQLAlchemyError, err:
            SESSION.rollback()
            output['output'] = 'notok'
            output['error'] = err.message
            httpcode = 500
    else:
        output['output'] = 'notok'
        output['error'] = 'Invalid input submitted'
        if form.errors:
            detail = []
            for error in form.errors:
                detail.append('%s: %s' % (error, '; '.join(form.errors[error])))
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


@APP.route('/tag/<pkgname>/', methods=['GET', 'POST'])
def tag_pkg(pkgname):
    """ Returns the tags associated with a package
    """
    if flask.request.method == 'GET':
        return get_tag_pkg(pkgname)
    elif flask.request.method == 'POST':
        return post_tag_pkg(pkgname)


@APP.route('/rating/<pkgname>/', methods=['GET', 'POST'])
def rating_pkg(pkgname):
    """ Returns the rating associated with a package
    """
    if flask.request.method == 'GET':
        return get_rating_pkg(pkgname)
    elif flask.request.method == 'POST':
        return post_rating_pkg(pkgname)


if __name__ == '__main__':  # pragma: no cover
    import sys
    sys.path.insert(0, '..')
    APP.debug = True
    APP.run()
