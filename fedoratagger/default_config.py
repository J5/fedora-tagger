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
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301  USA
#
# Refer to the README.rst and LICENSE files for full details of the license
# -*- coding: utf-8 -*-

"""
Default configuration for taggerapi
"""


# url to the database server:
DB_URL = 'sqlite:////var/tmp/taggerapi.sqlite'

# Resource prefix for tw2 middleware.
# In production this is usually '/tagger/_res/'
RES_PREFIX = '/_tw2_resources/'

# This is the secret salt used to hash IP addresses.
SECRET_SALT = 'CHANGE ME'
