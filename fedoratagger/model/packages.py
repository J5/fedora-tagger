# -*- coding: utf-8 -*-

import os
import json

from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import mapper, relation, backref

from fedoratagger.model import DeclarativeBase, metadata, DBSession

try:
    from hashlib import md5
except ImportError:
    import md5


def tag_sorter(tag1, tag2):
    """ The tag list for each package should be sorted in descending order by
    the total score, ties are broken by the number of votes cast and if there is
    still a tie, alphabetically by the tag.
    """
    for attr in ['total', 'votes', 'label']:
        result = cmp(getattr(tag1, attr), getattr(tag2, attr))
        if result != 0:
            return result
    return result

package_tag_association_table = Table(
    'package_tag_association', DeclarativeBase.metadata,
    Column('package_id', Integer, ForeignKey('package.id')),
    Column('tag_label_id', Integer, ForeignKey('tag_label.id')),
)

class Package(DeclarativeBase):
    __tablename__ = 'package'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    summary = Column(Unicode(1023), nullable=False)

    tags = relation('Tag', backref=('package'))
    tag_labels = relation(
        'TagLabel', backref=('packages'),
        secondary=package_tag_association_table
    )

    @property
    def icon(self):
        xapian_dir = '/var/cache/fedoracommunity/packages/xapian/search'
        if not os.path.exists(xapian_dir):
            return

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
        if len(matches) == 0: return None
        result = json.loads(matches[0].document.get_data())
        return "/packages/images/icons/%s.png" % result['icon']

    def __unicode__(self):
        return self.name

    def __json__(self):
        """ JSON.. kinda. """
        return {
            self.name: [
                tag.__json__() for tag in sorted(self.tags, tag_sorter)
                if not tag.banned
            ]
        }

    def __jit_data__(self):
        return {
            'hover_html' :
            u"<h2>Package: {name}</h2><ul>" + \
            " ".join([
                "<li>{tag.label.label} - {tag.like} / {tag.dislike}</li>".format(
                    tag=tag) for tag in self.tags
            ]) + "</ul>"
        }


class TagLabel(DeclarativeBase):
    __tablename__ = 'tag_label'
    id = Column(Integer, primary_key=True)
    label = Column(Unicode(255), nullable=False)
    tags = relation('Tag', backref=('label'))

    def __unicode__(self):
        return self.label


class Tag(DeclarativeBase):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('package.id'))
    label_id = Column(Integer, ForeignKey('tag_label.id'))
    votes = relation('Vote', backref=('tag'))

    like = Column(Integer, default=1)
    dislike = Column(Integer, default=0)

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

    def __json__(self):
        return {
            'tag': self.label.label,
            'like': self.like,
            'dislike': self.dislike,
            'total': self.total,
            'votes': self.total_votes,
        }

    def __jit_data__(self):
        return {
            'hover_html' :
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


class FASUser(DeclarativeBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), nullable=False)
    votes = relation('Vote', backref=('user'))
    email = Column(Unicode(255), default=None)

    @property
    def total_votes(self):
        return len(self.votes)

    @property
    def rank(self):

        if self.username == 'anonymous':
            return -1

        # TODO - there's a more optimal way to do this in SQL land.
        users = FASUser.query.filter(FASUser.username!='anonymous').all()
        users.sort(lambda x, y: cmp(x.total_votes, y.total_votes), reverse=True)

        return users.index(self) + 1

    @property
    def gravatar_sm(self):
        s=32
        d='mm'
        email = self.email if self.email else "whatever"
        hash = md5(email).hexdigest()
        url = "http://www.gravatar.com/avatar/%s?s=%i&d=%s" % (hash, s, d)
        return "<img src='%s'></img>" % url


    def __json__(self):
        return {
            'username': self.username,
            'votes': self.total_votes,
            'rank': self.rank,
        }
