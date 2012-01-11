import tw2.core
import tw2.forms
import random

from sqlalchemy import func

import fedoratagger.model as m
from fedoratagger.widgets.voting import TagWidget

def pick(tags, N, tags_voted_for):
    """ Select a subset of tags I haven't voted on yet. """


    if len(tags) <= N:
        return sorted(tags, m.packages.tag_sorter, reverse=True)

    unvoted = filter(lambda t: t not in tags_voted_for, tags)
    if len(unvoted) >= N:
        # If we haven't voted on at least N tags yet, return the top N
        return sorted(unvoted, m.packages.tag_sorter, reverse=True)[:N]
    else:
        # Otherwise, return those we haven't voted on yet, plus a random
        # sample of the ones we *have* voted on.
        already_voted = list(set(tags) - set(unvoted))
        return unvoted + random.sample(already_voted, N - len(unvoted))


def select_random_package(tags_voted_for):
    """ Select a random package based on a complicated set of rules """

    return m.Package.query.order_by(func.random()).first()


class CardWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    N = tw2.core.Param("Number of tags to show", default=5)
    package = tw2.core.Param(default=None)
    tags = tw2.core.params.Variable()
    css_class = 'card'

    template = 'fedoratagger.widgets.templates.card'

    def prepare(self):
        super(CardWidget, self).prepare()

        user = m.get_user()
        tags_voted_for = [v.tag for v in user.votes]

        if not self.package:
            self.package = select_random_package(tags_voted_for)

        allowed_tags = filter(lambda t: not t.banned, self.package.tags)

        if len(allowed_tags) >= self.N:
            picked_tags = random.sample(allowed_tags, self.N)
        else:
            picked_tags = allowed_tags

        self.tags = [TagWidget(tag=tag) for tag in picked_tags]
        self.tags[0].css_class += " selected"
