#!/usr/bin/env python
#
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

import warnings
warnings.catch_warnings()
warnings.simplefilter("ignore")

from os.path import abspath, sep
import simplejson

from paste.deploy import appconfig
from pylons import config
from fedoratagger.config.environment import load_environment

prefix = abspath(sep.join(__file__.split(sep)[:-1]))
conf = appconfig('config:%s/development.ini' % prefix)

load_environment(conf.global_conf, conf.local_conf)

import fedoratagger.model as m
m.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

from fedoratagger.lib.utils import dump2json
print simplejson.dumps(dump2json())
