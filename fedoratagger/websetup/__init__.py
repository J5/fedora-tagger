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
"""Setup the fedora-tagger application"""

import logging

from fedoratagger.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

from schema import setup_schema
import bootstrap

def setup_app(command, conf, vars):
    """Place any commands to setup fedoratagger here"""
    load_environment(conf.global_conf, conf.local_conf)
    setup_schema(command, conf, vars)
    bootstrap.bootstrap(command, conf, vars)
