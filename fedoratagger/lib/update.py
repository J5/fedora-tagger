# -*- coding: utf-8 -*-
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README.rst and LICENSE files for full details of the license
""" Update the fedora-tagger DB from other sources.

Notably, koji and pkgdb.

Over time, Fedora Packagers will add new packages to Fedora.  Tagger
needs to find out about them from the authoritative sources.
"""

from paste.deploy.converters import asbool

import argparse
import commands
import tempfile
import urllib
import sqlite3
import os
import shutil

from kitchen.text.converters import to_unicode

from sqlalchemy.orm.exc import NoResultFound

# Relative import
import model as m

import fedoratagger as ft

import logging
log = logging.getLogger("fedoratagger-update-db")
log.setLevel(logging.DEBUG)
logging.basicConfig()


def get_yum_query(require=True):
    log.info("Building yum query object")
    try:
        import yum
    except ImportError as e:
        if require:
            raise
        else:
            log.warn("Could not import yum.  Summaries not available.")
            log.warn(str(e))
            return None

    class YumQuery(yum.YumBase):

        def __init__(self):
            yum.YumBase.__init__(self)
            self.setCacheDir()
            self._pl = self.doPackageLists('all')

        def summary(self, name):

            def exacts(section):
                exactmatch, matched, unmatched = yum.packages.parsePackages(
                    getattr(self._pl, section), [name])
                return yum.misc.unique(exactmatch)

            sections = ['installed', 'available', 'updates', 'extras']
            exactmatch = sum(map(exacts, sections), [])
            if exactmatch:
                return exactmatch[0].summary
            else:
                return ''

    return YumQuery()


def get_icons():
    """ Ridiculous.  get icons from J5's personal space.

    Deprecated (to say the least).
    """

    log.info("Getting icons.")
    root = os.path.sep.join(
        os.path.abspath(__file__).split(os.path.sep)[:-3]
    )
    cwd = os.getcwd()

    if os.path.exists(cwd + "/icons.tar.xz"):
        log.info("Icons have already been downloaded.")
    else:
        url = "http://johnp.fedorapeople.org/downloads/xapian/icons.tar.xz"
        log.info("Getting " + url)
        urllib.urlretrieve(url, cwd + "/icons.tar.xz")

    status, output = commands.getstatusoutput('tar xvf %s/icons.tar.xz' % cwd)
    if status != 0:
        raise Exception("Failed to decompress icons.")

    shutil.rmtree(root + "/fedoratagger/frontend/static/images/icons", True)
    shutil.move(cwd + '/icons', root + '/fedoratagger/public/images')


def import_pkgdb_tags():
    log.info("Importing pkgdb tags.")
    yumq = get_yum_query()
    repo = "F-18-i386-u"
    base_url = "https://admin.fedoraproject.org/pkgdb"
    url = base_url + "/lists/sqlitebuildtags/F-18-i386-u"
    f, fname = tempfile.mkstemp(suffix="-%s.db" % repo)
    urllib.urlretrieve(url, fname)

    conn = sqlite3.connect(fname)
    cursor = conn.cursor()
    cursor.execute('select * from packagetags')
    for row in cursor:
        name, tag, score = map(to_unicode, row)

        p = m.Package.query.filter_by(name=name)
        tl = m.TagLabel.query.filter_by(label=tag)
        if p.count() == 0:
            if yumq:
                summary = to_unicode(yumq.summary(name))
            else:
                # If we have no access to yum... oh well.
                summary = u''

            ft.SESSION.add(m.Package(name=name, summary=summary))

        if tl.count() == 0:
            ft.SESSION.add(m.TagLabel(label=tag))

        package = p.one()
        label = tl.one()

        t = m.Tag()
        t.package = package
        t.label = label
        ft.SESSION.add(t)

        if label not in package.tag_labels:
            package.tag_labels.append(label)

    conn.close()
    os.remove(fname)

    npacks = ft.SESSION.query(m.Package).count()
    ntags = ft.SESSION.query(m.Tag).count()

    log.info("Done with pkgdb import.")
    log.debug("Imported %i packages." % npacks)
    log.debug("Imported %i tags." % ntags)


def import_koji_pkgs():
    """ Get the latest packages from koji.  These might not have made it into
    yum yet, so we won't even check for their summary until later.
    """
    log.info("Importing koji packages")
    import koji
    session = koji.ClientSession("https://koji.fedoraproject.org/kojihub")
    count = 0
    packages = session.listPackages()
    log.info("Looking through %i packages from koji." % len(packages))
    for package in packages:
        name = to_unicode(package['package_name'])
        try:
            p = m.Package.by_name(ft.SESSION, name)
        except NoResultFound:
            log.debug(name + ' -')
            count += 1
            ft.SESSION.add(m.Package(name=name, summary=u''))

    log.info("Got %i new packages from koji (with no summaries yet)" % count)


def update_summaries(N=100):
    """ Some packages we get from koji before they're in yum.  Therefore, they
    exist in our DB for a while with a package name and can receive tags, but
    they do not yet have a summary.  Consequently, here we can periodically
    update their summary if they appear in yum.
    """
    log.info("Updating first %i packages which have no summary (w/ yum)" % N)

    yumq = get_yum_query()

    if not yumq:
        log.warn("No access to yum.  Aborting.")
        return

    query = ft.SESSION.query(m.Package).filter_by(summary=u'')
    log.info("There are %i such packages... hold on." % query.count())

    # We limit this to only getting the first N summaries, since querying yum
    # takes so long.
    count = 0
    total = query.count()
    packages = query.all()
    for package in packages:
        summary = to_unicode(yumq.summary(package.name))
        log.debug(package.name + ' - ' + summary)

        if summary:
            package.summary = summary
            count += 1
        else:
            package.summary = '(no summary)'

        if count > N:
            break

    log.info("Done updating summaries from yum.  %i of %i." % (count, total))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--summaries-to-process',
        dest='summaries_to_process',
        default=10,
        help="Number of summaries to process from yum.  Time intensive."
    )
    return parser.parse_args()

def main():
    args = parse_args()
    log.info("Starting up fedoratagger-update-db")
    #get_icons()
    import_pkgdb_tags()
    import_koji_pkgs()
    update_summaries(int(args.summaries_to_process))

    ft.SESSION.commit()

if __name__ == '__main__':
    main()
