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
"""Test suite for the TG app's models"""
from nose.tools import eq_

from fedoratagger import model
from fedoratagger.tests.models import ModelTest

class TestGroup(ModelTest):
    """Unit test case for the ``Group`` model."""
    klass = model.Group
    attrs = dict(
        group_name = u"test_group",
        display_name = u"Test Group"
        )


class TestUser(ModelTest):
    """Unit test case for the ``User`` model."""
    
    klass = model.User
    attrs = dict(
        user_name = u"ignucius",
        email_address = u"ignucius@example.org"
        )

    def test_obj_creation_username(self):
        """The obj constructor must set the user name right"""
        eq_(self.obj.user_name, u"ignucius")

    def test_obj_creation_email(self):
        """The obj constructor must set the email right"""
        eq_(self.obj.email_address, u"ignucius@example.org")

    def test_no_permissions_by_default(self):
        """User objects should have no permission by default."""
        eq_(len(self.obj.permissions), 0)

    def test_getting_by_email(self):
        """Users should be fetcheable by their email addresses"""
        him = model.User.by_email_address(u"ignucius@example.org")
        eq_(him, self.obj)


class TestPermission(ModelTest):
    """Unit test case for the ``Permission`` model."""
    
    klass = model.Permission
    attrs = dict(
        permission_name = u"test_permission",
        description = u"This is a test Description"
        )
