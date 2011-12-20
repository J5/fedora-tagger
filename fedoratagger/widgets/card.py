import tw2.core
import tw2.forms

import fedoratagger.model as m
from fedoratagger.widgets.voting import TagWidget

class CardWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    package = tw2.core.Param()
    tags = tw2.core.params.Variable()

    template = 'fedoratagger.widgets.templates.card'

    def prepare(self):
        super(CardWidget, self).prepare()
        self.tags = [TagWidget(tag=tag) for tag in self.package.tags]
