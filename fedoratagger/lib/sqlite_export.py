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

create_statement = """
create table packagetags (
    name        text,
    tag         text,
    score       integer,
    primary key (name, tag)
)
"""

insert_statement = """
insert into packagetags (name, tag, score)
values ('{name}', '{tag}', {score})
"""


def sqlitebuildtags():
    """ Return the raw contents of a sqlite3 dump of our tags """

    # initialize/clear database
    fd, db_filename = tempfile.mkstemp()
    os.close(fd)

    # Build our statements
    script = ';\n'.join(_prepare_sqlite_statements())

    # Execute them to the temp file
    with sqlite3.connect(db_filename) as conn:
        conn.executescript(script)

    # Read the raw contents back out and return
    f = open(db_filename, 'r')
    dump = f.read()
    f.close()
    os.unlink(db_filename)
    return dump


def _prepare_sqlite_statements():
    """ Yield SQL statements to create a sqlite3 dump of our tags. """

    # Avoid circular imports
    import fedoratagger as ft
    import fedoratagger.lib.model as m

    yield create_statement

    packages = ft.SESSION.query(m.Package).all()
    for package in packages:
        for tag in package.tags:
            yield insert_statement.format(
                name=package.name,
                tag=tag.label,
                score=tag.total,
            )
