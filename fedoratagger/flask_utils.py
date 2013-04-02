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
""" Various flask utilities used by both the API and the app. """

import base64
import datetime

import fedoratagger as ft
import fedoratagger.lib.model as m

def current_user(request):
    """ Given an instance of flask.request, return a FASUser instance.

    returns None if the provided Authorization header is invalid.
    """

    token = None
    username = None
    authenticated = False

    # TODO - should this raise an exception instead of returning None?
    if 'Authorization' in request.headers:
        base64string = request.headers['Authorization']
        base64string = base64string.split()[1].strip()
        userstring = base64.b64decode(base64string)
        (username, token) = userstring.split(':')
        user = m.FASUser.by_name(ft.SESSION, username)
        if user \
                and user.api_token == token \
                and user.api_date >= datetime.date.today():
            return user
    elif request.remote_addr:
        user = m.FASUser.get_or_create(ft.SESSION,
                                       request.remote_addr,
                                       anonymous=True)
        ft.SESSION.commit()
        return user

    return None
