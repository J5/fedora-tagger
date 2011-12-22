import tw2.core as twc
from tw2.jqplugins.ui import DialogWidget

import codecs
import docutils.examples


def hotkeys_readme():
    """ Pick the README.rst off of disk and render the hotkeys section """

    root = '/'.join(__file__.split('/')[:-2])
    fname = root + '/README.rst'
    with codecs.open(fname, 'r', 'utf-8') as f:
        rst = f.read()
        hotkeys = rst.split('.. hotkeys')[1]
        return docutils.examples.html_body(hotkeys)


class HotkeysDialog(DialogWidget):
    """ jQuery UI dialog for the hotkeys help. """

    id = 'hotkeys_dialog'
    options = {
        'title': 'Hotkeys',
        'autoOpen': False,
        'width': 350,
    }
    value = hotkeys_readme()


search_action_js = twc.JSLink(link="javascript/search.js")

class SearchDialog(DialogWidget):
    """ jQuery UI dialog for the searchbar. """

    id = 'search_dialog'
    resources = DialogWidget.resources + [search_action_js]
    options = {
        'title': 'Search for a package',
        'autoOpen': False,
        'width': 350,
        'modal': True,
    }
    value = """<input id="search_box"/>"""

add_js = twc.JSLink(link="javascript/add.js")

class AddTagDialog(DialogWidget):
    """ jQuery UI dialog for adding a new tag. """

    id = 'add_dialog'
    resources = DialogWidget.resources + [add_js]
    options = {
        'title': 'Add a new tag',
        'autoOpen': False,
        'width': 350,
        'modal': True,
    }
    value = """<input id="add_box"/>"""
