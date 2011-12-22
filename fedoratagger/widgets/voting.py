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

    @property
    def upcls(self):
        user = m.get_user()
        query = m.Vote.query.filter_by(user=user, tag=self.tag)
        if query.count() == 0:
            return ""

        if not query.one().like:
            return ""

        return "mod"

    @property
    def downcls(self):
        user = m.get_user()
        query = m.Vote.query.filter_by(user=user, tag=self.tag)
        if query.count() == 0:
            return ""

        if query.one().like:
            return ""

        return "mod"

    @property
    def textcls(self):
        user = m.get_user()
        query = m.Vote.query.filter_by(user=user, tag=self.tag)
        if query.count() == 0:
            return ""

        if query.one().like:
            return "up_text"

        return "down_text"
