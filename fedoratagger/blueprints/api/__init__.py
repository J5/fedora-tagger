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
from flask_fas_openid import FAS
from functools import wraps

import taggerlib
import forms as forms
import taggerlib.model as model

# Create the application.
APP = flask.Flask(__name__)
# set up FAS
APP.config.from_object('taggerapi.default_config')
if 'TAGGERAPI_CONFIG' in os.environ:  # pragma: no cover
    APP.config.from_envvar('TAGGERAPI_CONFIG')
APP.config['SECRET_KEY'] = 'asljdlkhkfhakdg'
APP.config['FAS_OPENID_CHECK_CERT'] = False
FAS = FAS(APP)
SESSION = taggerlib.create_session(APP.config['DB_URL'])


from taggerapi.api import API


APP.register_blueprint(API)


# pylint: disable=W0613
@APP.teardown_request
def shutdown_session(exception=None):
    """ Remove the DB session at the end of each request. """
    SESSION.remove()
