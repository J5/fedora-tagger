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
"""The application's model objects"""

import json
import os
from datetime import datetime

WITH_FEDMSG = True
try:
    import fedmsg
except ImportError:
    WITH_FEDMSG = False

from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, synonym
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Integer, Unicode

try:
    from hashlib import md5
except ImportError:
    import md5

from kitchen.text.converters import to_unicode


# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()


def create_tables(db_url, debug=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :arg debug, a boolean specifying wether we should have the verbose
    output of sqlalchemy or not.
    :return a session that can be used to query the database.
    """
    engine = create_engine(db_url, echo=debug)
    DeclarativeBase.metadata.create_all(engine)
    sessionmak = sessionmaker(bind=engine)
    return sessionmak()



def tag_sorter(tag1, tag2):
    """ The tag list for each package should be sorted in descending order by
    the total score, ties are broken by the number of votes cast and if there
    is still a tie, alphabetically by the tag.
    """
    for attr in ['total', 'votes', 'label']:
        result = cmp(getattr(tag1, attr), getattr(tag2, attr))
        if result != 0:
            return result
    return result


class YumTags(DeclarativeBase):
    """ Table packagetags to records simple association of package name
    with tags and the number of vote on the tag.
    """
    __tablename__ = 'packagetags'

    name = Column(Text, nullable=False, primary_key=True)
    tag = Column(Text, nullable=False, primary_key=True)
    score = Column(Integer)

    @classmethod
    def all(cls, session):
        """ Return all the information. """
        return session.query(cls).all()


class Package(DeclarativeBase):
    __tablename__ = 'package'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    summary = Column(Unicode(1023), nullable=False)

    tags = relation('Tag', backref=('package'))

    __table_args__ = (
        UniqueConstraint('name'),
    )

    def _get_xapian_data(self):
        xapian_dir = '/var/cache/fedoracommunity/packages/xapian/search'
        if not os.path.exists(xapian_dir):
            NO_XAP = '__no_xapian_available__'
            keys = ['icon', 'summary']
            dumb_data = dict([(key, NO_XAP) for key in keys])
            return dumb_data

        import xapian
        from fedoracommunity.search.utils import filter_search_string
        package_name = filter_search_string(self.name)
        search_db = xapian.Database(xapian_dir)
        enquire = xapian.Enquire(search_db)
        qp = xapian.QueryParser()
        qp.set_database(search_db)
        search_string = "Ex__%s__EX" % package_name
        query = qp.parse_query(search_string)
        enquire.set_query(query)
        matches = enquire.get_mset(0, 1)

        if len(matches) == 0:
            return None

        result = json.loads(matches[0].document.get_data())
        return result

    @property
    def icon(self):
        result = self._get_xapian_data()
        if result:
            return "/packages/images/icons/%s.png" % result['icon']

    @property
    def xapian_summary(self):
        result = self._get_xapian_data()
        if result:
            return result['summary']

    @classmethod
    def by_name(cls, session, pkgname):
        """ Returns the Package corresponding to the provided package
        name.

        :arg session: the session used to query the database
        :arg pkgname: the name of the package (string)
        :raise sqlalchemy.orm.exc.NoResultFound: when the query selects
            no rows.
        :raise sqlalchemy.orm.exc.MultipleResultsFound: when multiple
            rows are matching.
        """
        return session.query(cls).filter_by(name = pkgname).one()

    def __unicode__(self):
        return self.name

    def __json__(self, visited=None):
        """ JSON.. kinda. """
        cls_name = type(self).__name__
        visited = visited or []

        if cls_name in visited:
            return self.name

        # else

        return {
            self.name: [
                tag.__json__(visited=visited+[cls_name])
                for tag in sorted(self.tags, tag_sorter)
                if not tag.banned
            ]
        }

    def __jit_data__(self):
        return {
            'hover_html':
            u"<h2>Package: {name}</h2><ul>" + \
            " ".join([
                "<li>{tag.label.label} - {tag.like} / {tag.dislike}</li>"\
                .format(tag=tag) for tag in self.tags
            ]) + "</ul>"
        }


class TagLabel(DeclarativeBase):
    __tablename__ = 'tag_label'
    id = Column(Integer, primary_key=True)
    label = Column(Unicode(255), nullable=False)
    tags = relation('Tag', backref=('label'))

    __table_args__ = (
        UniqueConstraint('label'),
    )

    def __unicode__(self):
        return self.label

    @classmethod
    def get_or_insert(cls, session, tag):
        """ Retrieve a TagLabel from its label or create a new one.

        :arg session: the session used to query the database
        :arg pkgname: the name of the package (string)
        :raise sqlalchemy.orm.exc.NoResultFound: when the query selects
            no rows.
        :raise sqlalchemy.orm.exc.MultipleResultsFound: when multiple
            rows are matching.
        """
        try:
            taglabel = session.query(cls).filter_by(label = tag).one()
        except NoResultFound:
            taglabel = TagLabel(label=tag)
            session.add(taglabel)
            session.flush()
        return taglabel

    def __json__(self, visited=None):
        """ JSON.. kinda. """
        cls_name = type(self).__name__
        visited = visited or []

        if cls_name in visited:
            return self.label

        return {
            'label': self.label,
            'tags': [t.__json__(visited=visited+[cls_name])
                     for t in self.tags],
        }


class Tag(DeclarativeBase):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('package.id'))
    label_id = Column(Integer, ForeignKey('tag_label.id'))
    votes = relation('Vote', backref=('tag'))

    like = Column(Integer, default=1)
    dislike = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('package_id', 'label_id'),
    )

    @property
    def banned(self):
        """ We want to exclude some tags permanently.

        https://github.com/ralphbean/fedora-tagger/issues/16
        """

        return any([
            self.label.label.startswith('X-'),
            self.label.label == 'Application',
            self.label.label == 'System',
            self.label.label == 'Utility',
        ])

    @property
    def total(self):
        return self.like - self.dislike

    @property
    def total_votes(self):
        return self.like + self.dislike

    def __unicode__(self):
        return self.label.label + " on " + self.package.name

    def __json__(self, visited=None):
        cls_name = type(self).__name__
        visited = visited or []

        result = {
            'tag': self.label.label,
            'like': self.like,
            'dislike': self.dislike,
            'total': self.total,
            'votes': self.total_votes,
        }

        if not cls_name in visited:
            visited = visited + [cls_name]
            result.update({
                'label': self.label.__json__(visited),
                'package': self.package.__json__(visited),
            })

        return result

    def __jit_data__(self):
        return {
            'hover_html':
            u""" <h2>Tag: {label}</h2>
            <ul>
                <li>Likes: {like}</li>
                <li>Dislike: {dislike}</li>
                <li>Total: {total}</li>
                <li>Votes: {votes}</li>
            </ul>
            """.format(
                label=unicode(self),
                like=self.like,
                dislike=self.dislike,
                total=self.total,
                votes=self.votes,
            )
        }


class Vote(DeclarativeBase):
    __tablename__ = 'vote'
    id = Column(Integer, primary_key=True)
    like = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    __table_args__ = (
        UniqueConstraint('user_id', 'tag_id'),
    )

    def __json__(self, visited=None):
        cls_name = type(self).__name__
        visited = visited or []

        result = {
            'like': self.like,
        }

        if not cls_name in visited:
            visited = visited + [cls_name]
            result.update({
                'user': self.user.__json__(visited),
                'tag': self.tag.__json__(visited),
            })

        return result


class FASUser(DeclarativeBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), nullable=False)
    votes = relation('Vote', backref=('user'))
    email = Column(Unicode(255), default=None)
    notifications_on = Column(Boolean, default=True)
    _rank = Column(Integer, default=-1)

    @property
    def anonymous(self):
        return self.username == 'anonymous'

    @property
    def total_votes(self):
        return len(self.votes)

    @property
    def rank(self):
        _rank = self._rank

        if self.username == 'anonymous':
            return -1

        users = FASUser.query.filter(FASUser.username != 'anonymous').all()
        lookup = list(reversed(sorted(set([u.total_votes for u in users]))))
        rank = lookup.index(self.total_votes) + 1

        # If their rank has changed.
        changed = rank != _rank

        # And it didn't change to last place.  We check last_place only to try
        # and avoid spamming the fedmsg bus.  We have a number of users who have
        # logged in once, and never voted.  Everytime a *new* user logs in and
        # votes once, *all* the users in last place get bumped down one notch.
        # No need to spew that to the message bus.
        is_last = rank == len(lookup)

        if changed:
            self._rank = rank

        if WITH_FEDMSG and changed and not is_last:
            fedmsg.send_message(topic='user.rank.update', msg={
                'user': self,
            })

        return self._rank

    @property
    def gravatar_lg(self):
        return self._gravatar(s=140)

    @property
    def gravatar_md(self):
        return self._gravatar(s=64)

    @property
    def gravatar_sm(self):
        return self._gravatar(s=32)

    def _gravatar(self, s):
        # TODO -- remove this and use
        # fedora.client.fas2.AccountSystem().gravatar_url(
        #                                   self.username, size=s)
        #  - need to have faswho put the gravatar url in the metadata
        #  - need to have different size images available as defaults
        d = 'mm'
        email = self.email if self.email else "whatever"
        hash = md5(email).hexdigest()
        url = "http://www.gravatar.com/avatar/%s?s=%i&d=%s" % (hash, s, d)
        return "<img src='%s'></img>" % url

    def __json__(self, visited=None):
        cls_name = type(self).__name__
        visited = visited or []
        obj = {
            'username': self.username,
            'votes': self.total_votes,
            'rank': self._rank,
        }

        ## Let's just not send all this information along to fedmsg.  It is way
        ## too much to share the entire voting history of every user every time
        ## they vote.
        #if not (cls_name in visited or 'Vote' in visited):
        #    obj.update({
        #        'all_votes': [v.__json__(visited=visited+[cls_name])
        #                      for v in self.votes],
        #    })

        return obj
