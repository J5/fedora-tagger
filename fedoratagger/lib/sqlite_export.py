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
""" Functions for exporting sqlite build tags to bodhi's masher. """

import os
import tempfile
import sqlite3


create_statement = u"""
create table packagetags (
    name        text,
    tag         text,
    score       integer,
    primary key (name, tag)
)
"""


insert_statement = u"""
insert into packagetags (name, tag, score)
values (?, ?, ?)
"""


def sqlitebuildtags():
    """ Return the raw contents of a sqlite3 dump of our tags """

    # initialize/clear database
    fd, db_filename = tempfile.mkstemp()
    os.close(fd)

    # Build our statements
    rows = _prepare_sqlite_tuples()

    # Execute them to the temp file
    with sqlite3.connect(db_filename) as conn:
        conn.execute(create_statement)
        conn.executemany(insert_statement, rows)

    # Read the raw contents back out and return
    f = open(db_filename, 'r')
    dump = f.read()
    f.close()
    os.unlink(db_filename)
    return dump


def _prepare_sqlite_tuples():
    """ Yield tuples of values for a sqlite db. """

    # Avoid circular imports
    import fedoratagger as ft
    import fedoratagger.lib.model as m

    packages = ft.SESSION.query(m.Package).all()
    for package in packages:
        for tag in package.tags:
            yield (
                package.name,
                tag.label,
                tag.total,
            )
