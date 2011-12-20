import tw2.core
import tw2.forms

import fedoratagger.model as m

class TagWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    tag = tw2.core.Param()
    template = 'fedoratagger.widgets.templates.tag'
