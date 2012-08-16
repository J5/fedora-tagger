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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Refer to the README.rst and LICENSE files for full details of the license
"""Setup the fedora-tagger application"""

import logging
from tg import config
from paste.deploy.converters import asbool
from fedoratagger import model
import transaction
import commands
import tempfile
import urllib
import sqlite3
import os
import sys
import shutil
import warnings

from kitchen.text.converters import to_unicode

log = logging.getLogger()


def get_yum_query():
    yumq = None
    try:
        import yum

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

        yumq = YumQuery()
    except ImportError as e:
        if asbool(config.get('require_yum', True)):
            raise(e)
        else:
            warnings.warn("Could not import yum.  Summaries not available.")
            warnings.warn(str(e))

    return yumq


def get_icons():
    log.info("Getting icons.")
    root = os.path.sep.join(__file__.split(os.path.sep)[:-3])
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

    shutil.rmtree(root + "/fedoratagger/public/images/icons", True)
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

        p = model.Package.query.filter_by(name=name)
        tl = model.TagLabel.query.filter_by(label=tag)
        if p.count() == 0:
            if yumq:
                summary = to_unicode(yumq.summary(name))
            else:
                # If we have no access to yum... oh well.
                summary = u''

            log.debug(name + ' - ' + summary)
            model.DBSession.add(model.Package(name=name, summary=summary))

        if tl.count() == 0:
            model.DBSession.add(model.TagLabel(label=tag))

        package = p.one()
        label = tl.one()

        t = model.Tag()
        t.package = package
        t.label = label
        model.DBSession.add(t)

        if label not in package.tag_labels:
            package.tag_labels.append(label)


    conn.close()
    os.remove(fname)

    npacks = model.Package.query.count()
    ntags = model.Tag.query.count()

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
        p = model.Package.query.filter_by(name=name)
        if p.count() == 0:
            log.debug(name + ' -')
            count += 1
            model.DBSession.add(model.Package(name=name, summary=u''))

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

    query = model.Package.query.filter_by(summary=u'')
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


def remove_duplicates():
    """ lmacken discovered that sometimes (under conditions we don't
    understand), packages get added to the DB twice.  Here, we detect and remove
    them.
    """

    log.info("Looking into any duplicates")
    removed = []  # For book keeping

    all_packages = model.Package.query.all()

    for package in all_packages:

        if package.name in removed:
            continue

        query = model.Package.query.filter_by(name=package.name)

        if query.count() > 1:

            # Then remove all the duplicates, leaving this package.
            for dupe in query.all()[1:]:
                removed.append(dupe.name)
                model.DBSession.delete(dupe)

    log.info("Found and removed %i duplicates: %r" % (len(removed), removed))


def bootstrap(command, conf, vars):
    """Place any commands to setup fedoratagger here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        get_icons()
        import_pkgdb_tags()
        import_koji_pkgs()
        update_summaries(N=99999)

        remove_duplicates()

        transaction.commit()
    except IntegrityError:
        import traceback
        log.error(traceback.format_exc())
        transaction.abort()
        log.info('Continuing with bootstrapping...')

    # <websetup.bootstrap.after.auth>
