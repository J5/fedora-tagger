import tw2.core
import tg
import hashlib

photo_css = tw2.core.CSSLink(link='css/photo.css')

class UserWidget(tw2.core.Widget):
    """ Gravatar widget """

    resources = [photo_css]
    template = 'fedoratagger.widgets.templates.user'

    def avatar_link(self, s=140, d='mm'):
        email = tg.request.identity.get('email', 'Whoops')
        hash = hashlib.md5(email).hexdigest()
        return "http://www.gravatar.com/avatar/%s?s=%i&d=%s" % (hash, s, d)
