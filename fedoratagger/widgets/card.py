import tw2.core
import tw2.forms
import random

import fedoratagger.model as m
from fedoratagger.widgets.voting import TagWidget

def pick(tags):
    """ Select a subset of tags 'smartly'.  See the README. """

    if len(tags) <= 5:
        return sorted(tags, m.packages.tag_sorter, reverse=True)

    # Three most popular and two random others
    tags = sorted(tags, m.packages.tag_sorter, reverse=True)
    return tags[:3] + random.sample(tags[3:], 2)


class CardWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    package = tw2.core.Param()
    tags = tw2.core.params.Variable()
    css_class = 'card'

    template = 'fedoratagger.widgets.templates.card'

    def prepare(self):
        super(CardWidget, self).prepare()
        self.tags = [TagWidget(tag=tag) for tag in pick(self.package.tags)]
        self.tags[0].css_class += " selected"
