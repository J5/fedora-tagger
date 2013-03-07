#!/usr/bin/python

__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

from taggerapi import APP
from taggerapi.taggerlib import model

model.create_tables(APP.config['DB_URL'], debug=True)
