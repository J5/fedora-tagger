import tw2.core as twc
from tw2.jqplugins.ui import DialogWidget

import codecs
import docutils.examples


def hotkeys_readme():
    root = '/'.join(__file__.split('/')[:-2])
    fname = root + '/README.rst'
    with codecs.open(fname, 'r', 'utf-8') as f:
        rst = f.read()
        hotkeys = rst.split('.. hotkeys')[1]
        return docutils.examples.html_body(hotkeys)


class HotkeysDialog(DialogWidget):
    id = 'hotkeys_dialog'
    options = {
        'title': 'Hotkeys',
        'autoOpen': False,
        'width': 350,
    }
    value = hotkeys_readme()


search_action_js = twc.JSLink(link="javascript/search.js")

class SearchDialog(DialogWidget):
    id = 'search_dialog'
    resources = DialogWidget.resources + [search_action_js]
    options = {
        'title': 'Search for a package',
        'autoOpen': False,
        'width': 350,
        'modal': True,
    }
    value = """<input id="search_box"/>"""
