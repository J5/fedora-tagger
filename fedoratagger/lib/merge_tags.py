"""
Tagger need to that will go through the database and merge all
old upper-cased tags into lower-cased ones.
The script Should be run as:
FEDORATAGGER_CONFIG = /etc/fedora-tagger/fedora-tagger.cfg python /path/to/fedoratagger/lib/merge_tags.py

or

FEDORATAGGER_CONFIG = /etc/fedora-tagger/fedora-tagger.cfg fedoratagger-merge-tag -b y
"""

import argparse

import model as m
import fedoratagger as ft

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy import and_


def process_values():

    print "Finding duplicate values....."

    rows = ft.SESSION.query(func.min(m.Tag.id).label("id"), m.Tag.package_id,\
                            m.Tag.label,\
                          func.sum(m.Tag.like).label("like"),\
                          func.sum(m.Tag.dislike).label("dislike")).\
                      group_by(func.lower(m.Tag.label), m.Tag.package_id).\
                      having(func.count("*")>1).all()
    total = len(rows)
    c = 1
    for r in rows:
        print "[%i- %i] --> Merge values ### [Tag.id %i]" % (c, total, r.id)
        c += 1
        update = ft.SESSION.query(m.Tag).filter(m.Tag.id==r.id)
        update.update(
                       {"like": r.like, 
                        "dislike": r.dislike
                       }, synchronize_session='fetch'
                     )

        print "-----Deleting duplicate values.."
        duplicate = ft.SESSION.query(m.Tag.id, m.Tag.label).\
                       filter(and_(m.Tag.id != r.id,
                                   func.lower(m.Tag.label) == func.lower(r.label)),\
                                   m.Tag.package_id == r.package_id)

        duplicate.delete(synchronize_session='fetch')

        ft.SESSION.commit()

    print "Converting tags to lower-case..."
    lowercase = ft.SESSION.query(m.Tag).all()
    total = len(lowercase)
    c = 1
    for l in lowercase:
        to = func.lower(l.label)
        print "[%i - %i] -- [%s]" % (c, total, l.label)
        c += 1
        l.label = func.lower(l.label)

    ft.SESSION.commit()

    ft.SESSION.close()

def create_backup():
    try:
        print "Creating backup of table."
        engine.execute("CREATE TABLE bk_tag AS Select * from tag")
        ft.SESSION.commit()
        return True
    except:
        return False
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
         '-b', '--backup',
         dest='backup',
         default='y',
         help="Backup the table Tag. {y, n}")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.backup == "y":
        if create_backup():
            process_values()
        else:
            print "Unable to create backup."
    else:
        process_values()

if __name__ == '__main__':
    main()
    print "Finish.."
