import warnings

warnings.catch_warnings()
warnings.simplefilter("ignore")

import os
import sys

# This block provides support for the default virtualenv
# deployment pattern.  The option `--virtualenv=` on the
# `paster modwsgi_deploy` command line will skip this section entirely.
prev_sys_path = list(sys.path)

import site
site.addsitedir('/usr/local/pythonenv/tagger/lib/python2.7/site-packages')
site.addsitedir(os.path.expanduser('~/.virtualenvs/tagger/lib/python2.7/site-packages'))

#Move just added item to the front of the python system path.
#Not needed if modwsgi>=3.0. Uncomment next 6 lines.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)

sys.path[:0] = new_sys_path
#End of virtualenv support

# This adds your project's root path to the PYTHONPATH so that you can import
# top-level modules from your project path.  This is how TurboGears QuickStarted
# projects are laid out by default.
import os, sys
if os.path.isdir('/usr/local/turbogears/tagger'):
    sys.path.append('/usr/local/turbogears/tagger')

# Set the environment variable PYTHON_EGG_CACHE to an appropriate directory
# where the Apache user has write permission and into which it can unpack egg files.
    os.environ['PYTHON_EGG_CACHE'] = '/usr/local/turbogears/tagger/python-eggs'

from paste.deploy import appconfig
from pylons import config
from fedoratagger.config.environment import load_environment

try:
    conf = appconfig('config:/usr/local/turbogears/tagger/production.ini')
    print "Using production configuration"
except Exception, e:
    print "*" * 75
    print "    USING DEVELOPMENT CONFIGURATION"
    print "*" * 75
    conf = appconfig('config:' + os.path.abspath('development.ini'))

load_environment(conf.global_conf, conf.local_conf)

import fedoratagger.model as m
m.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

print """
 ____________________________
< welcome to the tagger shell >
 ----------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\\
                ||----w |
                ||     ||


Try typing something, like:

>>>  m.Package.query.all()
"""
