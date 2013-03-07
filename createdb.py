#!/usr/bin/python

from taggerapi import APP
from taggerapi.taggerlib import model

model.create_tables(APP.config['DB_URL'], True)
