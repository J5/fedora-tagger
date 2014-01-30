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
"""The WTForms used by the flask application"""


import flask
from flask.ext import wtf
from datetime import time
from datetime import datetime

from wtforms import ValidationError

import fedoratagger.lib.model as model


def validate_package(form, field):
    """ Validate if the package name provided exists really. """
    #model.Package.by_name(SESSION, field.data)
    pass


def validate_percentage(form, field):
    """ Validate if the field data contains a value between 0 and 100.
    """
    value = int(field.data)
    if value < 0 or value > 100:
        raise ValidationError('Input is not a percentage')


def validate_boolean(form, field):
    """ Validate that the input can be converted safely to a boolean
    value.
    """
    if int(field.data) not in [-1, 1]:
        raise ValidationError('Input must be either -1 (dislike) or 1 (like)')


class AddTagForm(wtf.Form):
    """ Form used to add a tag to a package. """
    pkgname = wtf.TextField('Package name',
                            [wtf.validators.Required(), validate_package])
    tag = wtf.TextField('Tag', [wtf.validators.Required()])


class AddRatingForm(wtf.Form):
    """ Form used to add a rating to a package. """
    pkgname = wtf.TextField('Package name',
                            [wtf.validators.Required(), validate_package]
                            )
    rating = wtf.IntegerField('Rating', [wtf.validators.Required(),
                              validate_percentage])


class ToggleUsageForm(wtf.Form):
    """ Form used when toggling usage on a package. """
    pkgname = wtf.TextField('Package name',
                            [wtf.validators.Required(), validate_package]
                            )


class VoteTagForm(wtf.Form):
    """ Form used to add a rating to a package. """
    pkgname = wtf.TextField('Package name',
                            [wtf.validators.Required(), validate_package]
                            )
    tag = wtf.TextField('Tag', [wtf.validators.Required()])
    vote = wtf.IntegerField('vote', [wtf.validators.Required(),
                            validate_boolean])
