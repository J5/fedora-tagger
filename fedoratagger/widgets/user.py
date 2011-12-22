import tw2.core
import tg
import hashlib

import fedoratagger.model as m

photo_css = tw2.core.CSSLink(link='css/photo.css')

class UserWidget(tw2.core.Widget):
    """ Gravatar widget """

    resources = [photo_css]
    template = 'fedoratagger.widgets.templates.user'

    def avatar_link(self, s=140, d='mm'):
        email = tg.request.identity.get('email', 'Whoops')
        hash = hashlib.md5(email).hexdigest()
        return "http://www.gravatar.com/avatar/%s?s=%i&d=%s" % (hash, s, d)

    @property
    def formatted_name(self):
        return tg.request.identity.get(
            'ircnick',
            self.username
        )

    @property
    def username(self):
        return tg.request.identity['username']

    @property
    def total_votes(self):
        user = m.get_user(self.username)
        return user.total_votes

    @property
    def rank(self):
        user = m.get_user(self.username)
        return user.rank
