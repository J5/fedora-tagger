# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in fedora-tagger.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""
import socket

from tg.configuration import AppConfig
from pylons.i18n import ugettext
from paste.deploy.converters import asbool

import fedoratagger
from fedoratagger import model
from fedoratagger.lib import app_globals, helpers

from fedora.tg2.utils import add_fas_auth_middleware
from bunch import Bunch
class MyAppConfig(AppConfig):
    # If we're deployed to Fedora's dev environment, use the production FAS
    if 'dev.phx2.fedoraproject.org' in socket.gethostname():
        fas_auth = Bunch(fas_url='https://admin-prod.fedoraproject.org/accounts/')
    add_auth_middleware = add_fas_auth_middleware
    tw2_initialized = False

    def add_tosca2_middleware(self, app):
        if self.tw2_initialized:
            return app

        from tg import config
        from tw2.core.middleware import Config, TwMiddleware
        default_tw2_config = dict( default_engine=self.default_renderer,
                                   translator=ugettext,
                                   auto_reload_templates=asbool(self.get('templating.mako.reloadfromdisk', 'false'))
                                   )
        res_prefix = config.get('fedoratagger.resource_path_prefix')
        if res_prefix:
            default_tw2_config['res_prefix'] = res_prefix
        if getattr(self, 'custom_tw2_config', None):
            default_tw2_config.update(self.custom_tw2_config)
        app = TwMiddleware(app, **default_tw2_config)
        self.tw2_initialized = True
        return app


base_config = MyAppConfig()
base_config.renderers = []

base_config.package = fedoratagger

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'mako'
base_config.renderers.append('mako')
#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = fedoratagger.model
base_config.DBSession = fedoratagger.model.DBSession
# Configure the authentication backend

# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
base_config.sa_auth.cookie_secret = "ChangeME"

base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession

# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# override this if you are using a different charset for the login form
base_config.sa_auth.charset = 'utf-8'

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'

base_config.use_toscawidgets2 = True
