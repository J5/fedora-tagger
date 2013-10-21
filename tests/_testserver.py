#!/usr/bin/python

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources
import sys

PORT, DB_URL = int(sys.argv[-2]), sys.argv[-1]
import fedoratagger
from fedoratagger.lib import create_session
fedoratagger.SESSION = create_session(DB_URL)
fedoratagger.APP.debug = True
fedoratagger.APP.run(port=PORT)
