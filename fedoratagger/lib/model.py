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
"""The application's model objects"""

import json
import os
from datetime import datetime

import pkgwat.api
import fedmsg

from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, synonym
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Integer, Unicode

from kitchen.text.converters import to_unicode

import fedora.client
fas = fedora.client.AccountSystem()

DeclarativeBase = declarative_base()


def create_tables(db_url, alembic_ini=None, debug=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg alembic_ini, path to the alembic ini file. This is necessary
        to be able to use alembic correctly, but not for the unit-tests.
    :arg debug, a boolean specifying wether we should have the verbose
    output of sqlalchemy or not.
    :return a session that can be used to query the database.
    """
    engine = create_engine(db_url, echo=debug)
    DeclarativeBase.metadata.create_all(engine)

    if alembic_ini is not None:  # pragma: no cover
        # then, load the Alembic configuration and generate the
        # version table, "stamping" it with the most recent rev:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config(alembic_ini)
        command.stamp(alembic_cfg, "head")

    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession


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
    __table_args__ = (
        UniqueConstraint('name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    summary = Column(UnicodeText(convert_unicode=False), nullable=False)
    _meta = Column(Unicode(255), server_default='{}', nullable=False)

    tags = relation('Tag', backref=('package'))
    ratings = relation('Rating', backref=('package'))
    usages = relation('Usage', backref=('package'))

    def rating(self, session):
        return session.query(func.avg(Rating.rating))\
            .filter_by(package_id=self.id).one()[0]

    def meta(self, session):
        meta = json.loads(self._meta or '{}')
        if not meta:
            try:
                meta = pkgwat.api.get(self.name)
                self._meta = json.dumps(meta)
                session.add(self)
                session.commit()
            except Exception as e:
                print "Failed to get meta: %r from fedora-packages" % self.name
                print str(e)

        return meta

    def icon(self, sess):
        # TODO - cache this in the db so we don't have to hit pkgwat.
        tmpl = "https://apps.fedoraproject.org/packages/images/icons/%s.png"
        return tmpl % (self.meta(sess).get('icon', None) or 'package_128x128')

    def xapian_summary(self, sess):
        return self.meta(sess).get('summary', None) or ''

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
        return session.query(cls).filter_by(name=pkgname).one()

    @classmethod
    def random(cls, session):
        """ Returns a random package from the database.

        :arg session: the session used to query the database
        :arg pkgname: the name of the package (string)
        """
        result = session.query(cls).order_by(func.random()).first()
        if not result:
            raise NoResultFound()
        return result

    @classmethod
    def all(cls, session):
        """ Returns all Package entries in the database.

        :arg session: the session used to query the database
        """
        return session.query(cls).all()

    @property
    def usage(self):
        return len(self.usages)

    def __unicode__(self):
        return self.name

    def __json__(self, session):
        """ JSON.. kinda. """

        tags = []
        for tag in self.tags:
            tags.append(tag.__json__())

        rating = Rating.rating_of_package(session, self.id) or -1
        result = {
            'name': self.name,
            'summary': self.summary,
            'tags': tags,
            'rating': int(rating),
            'usage': self.usage,
            'icon': self.icon,
        }

        return result

    def __tag_json__(self):

        tags = []
        for tag in self.tags:
            tags.append(tag.__json__())

        result = {
            'name': self.name,
            'tags': tags,
        }

        return result

    def __rating_json__(self, session):

        rating = Rating.rating_of_package(session, self.id) or -1
        result = {
            'name': self.name,
            'rating': float(rating),
        }

        return result

    def __usage_json__(self, session):
        return {
            'name': self.name,
            'usage': self.usage,
        }

    def __jit_data__(self):
        return {
            'hover_html':
            u"<h2>Package: {name}</h2><ul>" +
            " ".join([
                "<li>{tag.label.label} - {tag.like} / {tag.dislike}</li>"
                .format(tag=tag) for tag in self.tags
            ]) + "</ul>"
        }


class Tag(DeclarativeBase):
    __tablename__ = 'tag'
    __table_args__ = (
        UniqueConstraint('package_id', 'label'),
    )

    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('package.id'))
    label = Column(Unicode(255), nullable=False)
    votes = relation('Vote', backref=('tag'))

    like = Column(Integer, default=1)
    dislike = Column(Integer, default=0)

    @property
    def banned(self):
        """ We want to exclude some tags permanently.

        https://github.com/ralphbean/fedora-tagger/issues/16
        """

        return any([
            self.label.startswith('x-'),
            self.label == 'application',
            self.label == 'system',
            self.label == 'utility',
        ])

    @property
    def total(self):
        return self.like - self.dislike

    @property
    def total_votes(self):
        return self.like + self.dislike

    @classmethod
    def get(cls, session, package_id, label):
        return session.query(cls).filter_by(package_id=package_id
                                            ).filter_by(label=label).one()

    @classmethod
    def by_label(cls, session, label):
        return session.query(cls).filter_by(label=label).all()

    @classmethod
    def count_unique_label(cls, session):
        return session.query(func.count(distinct(cls.label))).first()[0]

    def __unicode__(self):
        return self.label + " on " + self.package.name

    def __pkg_json__(self):
        result = {
            'tag': self.label,
            'like': self.like,
            'dislike': self.dislike,
            'total': self.total,
            'votes': self.total_votes,
            'package': self.package.name
        }

        return result

    __json__ = __pkg_json__

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
    __table_args__ = (
        UniqueConstraint('user_id', 'tag_id'),
    )

    id = Column(Integer, primary_key=True)
    like = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    @classmethod
    def get(cls, session, user_id, tag_id):
        return session.query(cls).filter_by(user_id=user_id
                                            ).filter_by(tag_id=tag_id).one()

    @classmethod
    def get_votes_user(cls, session, user_id):
        return session.query(cls).filter_by(user_id=user_id).all()

    def __json__(self):

        result = {
            'like': self.like,
            'user': self.user.__json__(),
            'tag': self.tag.__json__(),
        }

        return result


class Usage(DeclarativeBase):
    __tablename__ = 'usage'
    __table_args__ = (
        UniqueConstraint('user_id', 'package_id'),
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    package_id = Column(Integer, ForeignKey('package.id'))

    @classmethod
    def get(cls, session, package_id, user_id):
        """ Return a specific user's usage of a specific package. """
        return session.query(cls)\
                .filter_by(package_id=package_id)\
                .filter_by(user_id=user_id).one()

    @classmethod
    def usage_of_package(cls, session, pkgid):
        """ Return the usage count of the package specified by a id

        :arg session: the session used to query the database
        :arg pkgid: the identifier of the package in the database
            (integer)
        """
        return session.query(cls).filter_by(package_id=pkgid).count()

    @classmethod
    def all(cls, session):
        """ Return the total usage of all the packages in the database.

        Returns a list of tuples of the form::

            [
                (Package1, total_usage),
                (Package2, total_usage),
                ...
            ]

        :arg session: the session used to query the database
        """
        subquery = session.query(
            cls.package_id.label('package_id'),
            func.count(cls.id).label('total_usage')
        ).group_by(cls.package_id).subquery()

        return session.query(Package, subquery.c.total_usage).filter(
            Package.id == subquery.c.package_id
        ).all()

    def __json__(self, session):
        return {
            'user': self.user.__json__(),
            'package': self.package.__json__(session),
        }


class Rating(DeclarativeBase):
    __tablename__ = 'rating'
    __table_args__ = (
        UniqueConstraint('user_id', 'package_id'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    package_id = Column(Integer, ForeignKey('package.id'))
    rating = Column(Integer, nullable=False)

    @classmethod
    def get(cls, session, package_id, user_id):
        """ Return a specific user's rating on a specific package. """
        return session.query(cls)\
                .filter_by(package_id=package_id)\
                .filter_by(user_id=user_id).one()

    @classmethod
    def rating_of_package(cls, session, pkgid):
        """ Return the average rating of the package specified by his
        package.id.

        :arg session: the session used to query the database
        :arg pkgid: the identifier of the package in the database
            (integer)
        """
        return session.query(func.avg(cls.rating)
                            ).filter_by(package_id=pkgid).one()[0]

    @classmethod
    def all(cls, session):
        """ Return the average rating of all the packages in the database.

        Returns a list of tuples of the form::

            [
                (Package1, average_rating),
                (Package2, average_rating),
                ...
            ]

        :arg session: the session used to query the database
        """
        subquery = session.query(
            cls.package_id.label('package_id'),
            func.avg(cls.rating).label('avg_rating')
        ).group_by(cls.package_id).subquery()

        return session.query(Package, subquery.c.avg_rating).filter(
            Package.id == subquery.c.package_id
        ).all()

    @classmethod
    def by_rating(cls, session, ratingscore):
        """ Return all the packages in the database having the specified
        rating.

        :arg session: the session used to query the database
        """
        subquery = session.query(
            cls.package_id.label('package_id'),
            func.avg(cls.rating).label('avg'),
        ).group_by(cls.package_id).subquery()

        return session.query(Package).filter(and_(
            Package.id == subquery.c.package_id,
            subquery.c.avg == ratingscore,
        )).all()

    def __json__(self, session):

        result = {
            # We type this to an int to avoid precision problems in json that
            # cascade into crypto problems between machines.
            # See https://github.com/fedora-infra/fedmsg/pull/201 for reference
            'rating': int(self.rating),
            'user': self.user.__json__(),
            'package': self.package.__json__(session),
        }

        return result


class FASUser(DeclarativeBase):
    __tablename__ = 'user'
    __table_args__ = (
        UniqueConstraint('username'),
    )

    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), nullable=False)

    votes = relation('Vote', backref=('user'))
    ratings = relation('Rating', backref=('user'))
    usages = relation('Usage', backref=('user'))

    email = Column(Unicode(255), default=None)
    notifications_on = Column(Boolean, default=True)
    _rank = Column(Integer, default=-1)
    score = Column(Integer, nullable=False, default=0)
    api_token = Column(String(45), default=None)
    api_date = Column(Date, default=datetime.today())
    anonymous = Column(Boolean, nullable=False, default=False)

    @property
    def total_votes(self):
        return len(self.votes)

    def uses(self, session, package):
        for usage in self.usages:
            if usage.package == package:
                return True
        return False

    def rank(self, session):
        _rank = self._rank

        if self.anonymous:
            return -1

        users = session.query(FASUser)\
                .filter(FASUser.username != 'anonymous').all()
        lookup = sorted(set([u.score for u in users]), reverse=True)
        rank = lookup.index(self.score) + 1

        # If their rank has changed.
        changed = (rank != _rank)

        # And it didn't change to last place.  We check last_place only to try
        # and avoid spamming the fedmsg bus.  We have a number of users who
        # have logged in once, and never voted.  Everytime a *new* user logs
        # in and votes once, *all* the users in last place get bumped down
        # one notch.
        # No need to spew that to the message bus.
        is_last = (rank == len(lookup))

        if changed:
            self._rank = rank
            session.add(self)
            session.commit()

        if changed and not is_last:
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
        url = fas.avatar_url(self.username, size=s, lookup_email=False)
        return "<img src='%s'></img>" % url

    @classmethod
    def get_or_create(cls, session, username, email=None,
                      anonymous=False):
        """ Get or Add a user to the database using its username.
        This function simply tries to find the specified username in the
        database and if that person is not known, add a new user with
        this username.

        :arg session: the session used to query the database.
        :arg username: the username of the user to search for or to
            create. In some cases it will be his IP address.
        :kwarg email: the email address to associate with this user.
        :kwarg anonymous: a boolean specifying if the user is anonymous
            or not.
        """
        try:
            user = session.query(cls).filter_by(username=username).one()
            if email:
                user.email = email
        except NoResultFound:
            user = FASUser(username=username,
                           email=email,
                           anonymous=anonymous)
            session.add(user)
            session.flush()
        return user

    @classmethod
    def top(cls, session, limit=10):
        """ Return the top contributors ordered by their scores.

        :arg session: the session used to query the database.
        :kwarg limit: the max number of user to return.
        """
        return session.query(cls
                            ).filter(FASUser.anonymous == False
                            ).order_by(FASUser.score.desc()
                            ).limit(limit
                            ).all()

    @classmethod
    def by_name(cls, session, username):
        """ Return the user based on the provided username.

        :arg session: the session used to query the database.
        :arg username: the username of the desired user.
        """
        return session.query(cls
                            ).filter(FASUser.username == username
                            ).filter(FASUser.anonymous == False
                            ).one()

    def __json__(self, visited=None):
        obj = {
            'username': self.anonymous and 'anonymous' or self.username,
            'votes': self.total_votes,
            'score': self.score,
            'rank': self._rank,
            'anonymous': self.anonymous,
        }

        return obj
