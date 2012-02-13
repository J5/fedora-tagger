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
from tg import config
import transaction

def setup_schema(command, conf, vars):
    """Place any commands to setup fedoratagger here"""
    # Load the models

    # <websetup.websetup.schema.before.model.import>
    from fedoratagger import model
    # <websetup.websetup.schema.after.model.import>

    
    # <websetup.websetup.schema.before.metadata.create_all>
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
    # <websetup.websetup.schema.after.metadata.create_all>
    transaction.commit()

    # Commented out since sqlalchemy migrate looks to not be in our production
    # environment.
    #from migrate.versioning.shell import main
    #from migrate.exceptions import DatabaseAlreadyControlledError
    #try:
    #    main(argv=['version_control'], url=config['sqlalchemy.url'], repository='migration', name='migration')
    #except DatabaseAlreadyControlledError:
    #    print 'Database already under version control'
