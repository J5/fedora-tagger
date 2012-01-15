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
"""WSGI middleware initialization for the fedora-tagger application."""

from fedoratagger.config.app_cfg import base_config
from fedoratagger.config.environment import load_environment

import tg
tg_version_tuple = tuple(map(int, tg.__version__.split('.')))

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory. 
# make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set fedora-tagger up with the settings found in the PasteDeploy configuration
    file used.
    
    :param global_conf: The global settings for fedora-tagger (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The fedora-tagger application with all the relevant middleware
        loaded.
    
    This is the PasteDeploy factory for the fedora-tagger application.
    
    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.
    
   
    """
    if tg_version_tuple < (2, 1):
        app_conf['wrap_app'] = base_config.add_tosca2_middleware

    app = make_base_app(global_conf, full_stack=True, **app_conf)
    
    # Wrap your base TurboGears 2 application with custom middleware here
    
    return app
