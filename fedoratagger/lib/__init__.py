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
"""Backend library"""

import base64
import random
import string
from datetime import date

import fedmsg

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound

import model

from sqlite_export import sqlitebuildtags


def create_session(db_url, debug=False, pool_recycle=3600):
    """ Create the Session object to use to query the database.

    :arg db_url: URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :arg debug: a boolean specifying wether we should have the verbose
        output of sqlalchemy or not.
    :return a Session that can be used to query the database.
    """
    engine = create_engine(db_url, echo=debug, pool_recycle=pool_recycle)
    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession


def add_tag(session, pkgname, tag, user):
    """ Add a provided tag to the specified package. """

    tag = tag.lower()

    package = model.Package.by_name(session, pkgname)
    try:
        tagobj = model.Tag.get(session, package.id, tag)
        tagobj.like += 1
        user.score += 1
    except NoResultFound:

        # If no such tag exists, create a new one.  But first..
        if blacklisted(tag):
            raise ValueError("'%s' is not allowed." % tag)

        tagobj = model.Tag(package_id=package.id, label=tag)
        session.add(tagobj)
        session.flush()
        user.score += 2
    voteobj = model.Vote(user_id=user.id, tag_id=tagobj.id, like=True)
    session.add(user)
    session.add(voteobj)
    session.flush()

    fedmsg.publish('tag.create', msg=dict(
        tag=tagobj,
        vote=voteobj,
        user=user,
    ))

    return 'Tag "%s" added to the package "%s"' % (tag, pkgname)


def set_usage(session, pkgname, user, usage):
    """ Set the usage marker for a specified package. """
    package = model.Package.by_name(session, pkgname)

    try:
        # Try to change an existing usage first.
        usageobj = model.Usage.get(session, package_id=package.id,
                                   user_id=user.id)
        if usage:
            return 'You already do not use %s' % pkgname
        session.delete(usageobj)
        message = 'You no longer use %s' % pkgname
        usage = False
    except NoResultFound:
        # If no usage was found, we need to add a new one.
        if not usage:
            return 'You already use %s' % pkgname
        usageobj = model.Usage(package_id=package.id, user_id=user.id)
        session.add(usageobj)
        message = 'Marked that you use %s' % pkgname
        session.add(usageobj)
        usage = True

    session.flush()
    fedmsg.publish('usage.toggle', msg=dict(
        user=user.__json__(session),
        package=package.__json__(session),
        usage=usage,
    ))

    return message


def add_rating(session, pkgname, rating, user):
    """ Add the provided rating to the specified package. """
    package = model.Package.by_name(session, pkgname)

    try:
        # Try to change an existing rating first.
        ratingobj = model.Rating.get(session, package_id=package.id,
                                     user_id=user.id)

        if ratingobj.rating == rating:
            message = 'Rating on package "%s" did not change' % (
                pkgname)
        else:
            ratingobj.rating = rating
            message = 'Rating on package "%s" changed to "%s"' % (
                pkgname, rating)

    except NoResultFound:
        # If no rating was found, we need to add a new one.
        ratingobj = model.Rating(package_id=package.id, user_id=user.id,
                                 rating=rating)
        session.add(ratingobj)
        user.score += 1
        session.add(user)
        message = 'Rating "%s" added to the package "%s"' % (rating, pkgname)

    session.add(ratingobj)
    session.flush()

    fedmsg.publish('rating.update', msg=dict(
        rating=ratingobj.__json__(session),
    ))

    return message


def add_vote(session, pkgname, tag, vote, user):
    """ Cast a vote for a tag of a specified package. """
    try:
        package = model.Package.by_name(session, pkgname)
        tagobj = model.Tag.get(session, package.id, tag)
    except NoResultFound, err:
        raise TaggerapiException('This tag could not be found associated'
                                 ' to this package')
    verb = 'changed'
    try:
        # if the vote already exist, replace it
        voteobj = model.Vote.get(session, user_id=user.id,
                                 tag_id=tagobj.id)
        if voteobj.like == vote:
            return 'Your vote on the tag "%s" for the package "%s" did ' \
                   'not change' % (tag, pkgname)
        else:
            if voteobj.like:
                tagobj.like -= 1
                tagobj.dislike += 1
            else:
                tagobj.dislike -= 1
                tagobj.like += 1
            voteobj.like = vote
    except NoResultFound:
        # otherwise, create it
        verb = 'added'
        voteobj = model.Vote(user_id=user.id, tag_id=tagobj.id, like=vote)
        if vote:
            tagobj.like += 1
        else:
            tagobj.dislike += 1
        user.score += 0.5

    session.add(user)
    session.add(tagobj)
    session.add(voteobj)
    session.flush()

    fedmsg.publish('tag.update', msg=dict(
        tag=tagobj,
        vote=voteobj,
        user=user,
    ))

    return 'Vote %s on the tag "%s" of the package "%s"' % (verb, tag, pkgname)


def statistics(session):
    """ Handles the /statistics/ path.

    Returns a dictionnary of statistics on tagged packages.
    """

    packages = model.Package.all(session)
    n_tags = model.Tag.count_unique_label(session)
    raw_data = dict([(p.name, len(p.tags)) for p in packages])

    n_packs = len(raw_data)
    no_tags = len([v for v in raw_data.values() if not v])
    with_tags = n_packs - no_tags

    tags_per_package = 0
    if n_packs:
        tags_per_package = sum([len(p.tags) for p in packages]) \
            / float(n_packs)

    tags_per_package_no_zeroes = 0
    if with_tags:
        tags_per_package_no_zeroes = sum([len(p.tags) for p in packages]) \
            / float(with_tags)

    n_votes = float(session.query(model.Vote).count())

    if n_tags:
        avg_votes_per_tag = n_votes / n_tags
    else:
        avg_votes_per_tag = 0

    if n_packs:
        avg_votes_per_package  = n_votes / n_packs
        most_votes_per_tag = max(raw_data.values())
    else:
        avg_votes_per_package = 0
        most_votes_per_tag = 0

    return {
        'summary': {
            'total_packages': n_packs,
            'total_unique_tags': n_tags,
            'no_tags': no_tags,
            'with_tags': with_tags,
            'tags_per_package': tags_per_package,
            'tags_per_package_no_zeroes': tags_per_package_no_zeroes,
            'avg_votes_per_tag': avg_votes_per_tag,
            'avg_votes_per_package': avg_votes_per_package,
            'most_votes_per_tag': most_votes_per_tag,
        },
    }


def statistics_by_user(session, user, fields="all"):
    """ Handles the /statistics/<user> path.

    Returns a dictionnary of statistics of an user votes.
    """
    votes = model.Vote.get_votes_user(session, user.id)

    votes_like = votes_dislike = dict()
    total_like = total_dislike = total_votes = 0

    if votes:
        votes_like = \
            [(v.tag.package.name, v.tag.label) for v in votes if v.like]
        votes_dislike = \
            [(v.tag.package.name, v.tag.label) for v in votes if not v.like]

        total_like = len(votes_like)
        total_dislike = len(votes_dislike)
        total_votes = total_like + total_dislike

    if fields == "all":
        return dict(like=votes_like, total_like=total_like,
                    dislike=votes_dislike, total_dislike=total_dislike,
                    total=total_votes)
    else:
        return dict(total_like=total_like,
                    total_dislike=total_dislike,
                    total=total_votes)

def leaderboard(session):
    """ Handles the /leaderboard/ path.

    Returns a dictionnary of the top 10 contributors.
    """

    contributors = model.FASUser.top(session)
    cnt = 1
    output = {}
    for contributor in contributors:
        output[cnt] = {'name': contributor.username,
                       'gravatar': contributor.gravatar_sm,
                       'score': contributor.score
                       }
        cnt += 1
    return output


def score(session, username):
    """ Return the score of a specific user.
    """
    contributor = model.FASUser.by_name(session, username)
    output = {'name': contributor.username,
              'gravatar': contributor.gravatar_sm,
              'score': contributor.score
              }
    return output


def generate_api_token(size=30):
    """ Generate a random string used as token to access the API
    remotely.

    :kwarg: size, the size of the token to generate, defaults to 30
        chars.
    :return: a string, the API token for the user.
    """
    token = '%s##' % base64.b64encode('taggerapi')
    return '%s%s' % (token,
                     ''.join(random.choice(
                             string.ascii_lowercase)
                             for x in range(size - len(token))))


def get_api_token(session, user):
    """ Generate an API token for the specified user.
    """
    contributor = model.FASUser.get_or_create(session,
                                              username=user.username,
                                              email=user.email)
    contributor.api_token = generate_api_token(40)
    contributor.api_date = date.today()
    session.add(contributor)
    session.flush()
    return {'name': contributor.username,
            'token': contributor.api_token}


class TaggerapiException(Exception):
    """ Generic exception class used to manage exception from taggerapi. """
    pass


def blacklisted(tag):
    """ Return true if the given string is blacklisted (not allowed) """
    return tag in _dirty_words


def _load_dirty_words():
    import os
    sep = os.path.sep
    dirname = sep.join(os.path.abspath(__file__).split(sep)[:-2])
    with open(dirname + "/dirtywords.txt") as f:
        return [line.strip() for line in f.readlines()]

_dirty_words = _load_dirty_words()
