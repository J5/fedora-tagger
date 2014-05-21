import argparse

import model as m
import fedoratagger as ft

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
dburi = ft.APP.config['DB_URL']
engine = sqlalchemy.create_engine(dburi)

def process_values():
    print "Finding duplicate values....."
    rsum = engine.execute("SELECT min(tag.id) as id, sum(tag.like) as like,\
                      sum(tag.dislike) as dislike FROM tag \
                      GROUP  BY lower(tag.label), tag.package_id \
                      HAVING COUNT(*) > 1 \
                      ORDER  BY COUNT(*) DESC")

    tag1 = ft.SESSION.query(m.Tag).instances(rsum)
    c = 0
    for s in tag1:
        print "Updating the first record...."
        update = ft.SESSION.query(m.Tag).filter(m.Tag.id==s.id)
        update.update({"like": s.like, "dislike": s.dislike})
        c+=1

    if c > 0:
        ft.SESSION.commit()

        print "Deleting duplicate values..."
        rdelete ="delete from tag where tag.id in (select b.id  from tag b ,\
              (select package_id,lower(label) as label, min(id) as id \
                       from tag GROUP  BY lower(label), package_id \
                       HAVING COUNT(*) > 1 ORDER  BY COUNT(*) DESC) a \
                       where a.package_id = b.package_id \
                       and lower(a.label) = lower(b.label) \
                       and a.id != b.id)"
        engine.execute(rdelete)
        ft.SESSION.commit()

        print "Converting tags to lower-case..."

        rows = ft.SESSION.query(m.Tag).all()
        for r in rows:
            r.label = func.lower(r.label)

        ft.SESSION.commit()
    else:
        print "No such values."

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
         help="backup.")
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
