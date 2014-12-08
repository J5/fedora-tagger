"""
Tagger need to remove the packages in retired status.
Is that the script Should be run as:

FEDORATAGGER_CONFIG = /etc/fedora-tagger/fedora-tagger.cfg python /path/to/fedoratagger/lib/retired.py

or

FEDORATAGGER_CONFIG = /etc/fedora-tagger/fedora-tagger.cfg fedoratagger-remove-pkgs -s Retired
"""
import requests
import json

import argparse
import model as m
import fedoratagger as ft

import sqlalchemy

import logging

log = logging.getLogger("fedoratagger-remove")
log.setLevel(logging.DEBUG)
logging.basicConfig()

PKGDB_URL = 'https://admin.fedoraproject.org/pkgdb/api/packages'

def get_packages(status):
    log.info('Retrieve the list of %s packages.' % status)
    total = 1
    page = 1
    packages = []
    while page <= total:
        args = {
            'status': status,
            'page': page,
        }
        r = requests.get(PKGDB_URL, params=args)
        output = json.loads(r.text)
        if hasattr(output, 'error'):
            log.error(output['error'])
            return packages

        total = output['page_total']
        for pkg in output['packages']:
            packages.append(pkg['name'])
        page += 1

    return packages

def del_packages(status):

    log.info('Deleting packages.')

    s = 0
    e = 100
    pkgs = get_packages(status)
    l = len(pkgs)
    while (pkgs[s:e]):
        log.info('searching packages [%i] to [%i] of [%i]' % (s, e, l))
        package = ft.SESSION.query(m.Package).filter(m.Package.name.in_(pkgs[s:e]))
        s = e
        e = e + 100

        for r in package:
            tag = ft.SESSION.query(m.Tag).filter(m.Tag.package_id == r.id)
            usage = ft.SESSION.query(m.Usage).filter(m.Usage.package_id == r.id)
            rating = ft.SESSION.query(m.Rating).filter(m.Rating.package_id == r.id)
            for t in tag:
                vote = ft.SESSION.query(m.Vote).filter(m.Vote.tag_id == t.id)
                vote.delete()
            tag.delete()
            usage.delete()
            rating.delete()
        package.delete(synchronize_session='fetch')

        ft.SESSION.commit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
          '-s', '--status',
          dest='status',
          default='Retired',
          help="Restrict to status. {Approved, Retired, Orphaned}"
         )
    return parser.parse_args()

def main():

    args = parse_args()

    del_packages(args.status.title())

if __name__ == '__main__':
    main()
