import tw2.core
import tw2.forms
import tw2.jqplugins.gritter

import fedoratagger.model as m

voting_js = tw2.core.JSLink(link="javascript/voting.js")

class TagWidget(tw2.forms.LabelField):
    """ Tiny Voting Widget """

    css_class = ""
    resources = [voting_js] + tw2.jqplugins.gritter.gritter_resources
    tag = tw2.core.Param()
    template = 'fedoratagger.widgets.templates.tag'
