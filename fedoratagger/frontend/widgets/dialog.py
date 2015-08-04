# This file is a part of Fedora Tagger
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Refer to the README.rst and LICENSE files for full details of the license
import tw2.core as twc
from tw2.jqplugins.ui import DialogWidget

import codecs
import docutils.examples


def hotkeys_readme():
    """ Pick the README.rst off of disk and render the hotkeys section """

    root = '/'.join(__file__.split('/')[:-4])
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
        'width': 550,
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
        'title': 'Add new tags (comma-separated)',
        'autoOpen': False,
        'width': 350,
        'modal': True,
    }
    value = """<input id="add_box"/><div id="info1" class="info">Press Enter to save tag</div>"""

class LeaderboardDialog(DialogWidget):
    """ jQuery UI dialog for showing the leaderboard. """

    id = 'leaderboard_dialog'
    options = {
        'title': 'Leaderboard',
        'autoOpen': False,
        'width': 350,
        'modal': True,
    }

class StatisticsDialog(DialogWidget):
    """ jQuery UI dialog for showing the statistics. """

    id = 'statistics_dialog'
    options = {
        'title': 'Statistics',
        'autoOpen': False,
        'width': 350,
        'modal': True,
    }
