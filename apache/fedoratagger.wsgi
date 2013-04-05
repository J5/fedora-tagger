import __main__
__main__.__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4', 'mako >= 0.4']
import pkg_resources

import os
os.environ['FEDORATAGGER_CONFIG'] = '/etc/fedoratagger/fedoratagger.cfg'

import fedoratagger
application = fedoratagger.APP
#application.debug = True  # Nope.  Be careful!
