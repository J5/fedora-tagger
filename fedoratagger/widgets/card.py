import tw2.core
import tw2.forms
import random
import tw2.jqplugins.gritter

from sqlalchemy import func

import fedoratagger.model as m
from fedoratagger.widgets.voting import TagWidget

def pick(tags, N):
    """ Select a subset of tags I haven't voted on yet. """

    if len(tags) <= N:
        return sorted(tags, m.packages.tag_sorter, reverse=True)

    # TODO -- we need a way of selecting only tags I haven't voted on yet

    # Just scrap all the fancy logic and return a random sample of tags
    return random.sample(tags, N)


def select_random_package():
    """ Select a random package based on a complicated set of rules """

    return m.Package.query.order_by(func.random()).first()


class CardWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    N = tw2.core.Param("Number of tags to show", default=5)
    package = tw2.core.Param(default=None)
    tags = tw2.core.params.Variable()
    css_class = 'card'
    resources = tw2.jqplugins.gritter.gritter_resources

    template = 'fedoratagger.widgets.templates.card'

    def prepare(self):
        super(CardWidget, self).prepare()

        user = m.get_user()

        if not self.package:
            self.package = select_random_package()

        allowed_tags = filter(lambda t: not t.banned, self.package.tags)

        # Weird corner cases of obsoleted packages, etc.
        while not self.package.xapian_summary:
            self.package = select_random_package()
            allowed_tags = filter(lambda t: not t.banned, self.package.tags)

        if len(allowed_tags) >= self.N:
            picked_tags = random.sample(allowed_tags, self.N)
        else:
            picked_tags = allowed_tags

        self.tags = [TagWidget(tag=tag) for tag in picked_tags]
        if self.tags:
            self.tags[0].css_class += " selected"
