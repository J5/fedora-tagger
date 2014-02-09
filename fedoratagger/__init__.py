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

import os

from tw2.core.middleware import make_middleware as make_tw2_middleware

import flask
from flask_fas_openid import FAS
from flask.ext.mako import MakoTemplates

from fedoratagger.lib import create_session

# Create the application.
APP = flask.Flask(__name__)
# set up FAS
APP.config.from_object('fedoratagger.default_config')
if 'FEDORATAGGER_CONFIG' in os.environ:  # pragma: no cover
    APP.config.from_envvar('FEDORATAGGER_CONFIG')
APP.config['FAS_OPENID_CHECK_CERT'] = False
FAS = FAS(APP)
mako = MakoTemplates(APP)
SESSION = create_session(APP.config['DB_URL'])

from fedoratagger.api import API
from fedoratagger.frontend import FRONTEND


APP.register_blueprint(API)
APP.register_blueprint(FRONTEND)
APP.wsgi_app = make_tw2_middleware(
    APP.wsgi_app,
    res_prefix=APP.config['RES_PREFIX'],
)


# pylint: disable=W0613
@APP.teardown_request
def shutdown_session(exception=None):
    """ Remove the DB session at the end of each request. """
    SESSION.remove()
