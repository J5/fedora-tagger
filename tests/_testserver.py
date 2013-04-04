#!/usr/bin/python

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources
import sys

PORT, DB_URL = int(sys.argv[-2]), sys.argv[-1]
from fedoratagger import APP
APP.config['DB_URL'] = DB_URL
APP.run(port=PORT)
