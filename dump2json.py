#!/usr/bin/env python

import warnings
warnings.catch_warnings()
warnings.simplefilter("ignore")

from os.path import abspath, sep
import simplejson

from paste.deploy import appconfig
from pylons import config
from fedoratagger.config.environment import load_environment

prefix = abspath(sep.join(__file__.split(sep)[:-1]))
conf = appconfig('config:%s/development.ini' % prefix)

load_environment(conf.global_conf, conf.local_conf)

import fedoratagger.model as m
m.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

from fedoratagger.lib.utils import dump2json
print simplejson.dumps(dump2json())
