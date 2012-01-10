import os
os.environ['PYTHON_EGG_CACHE'] = '/var/cache/fedoratagger/.egg_cache'
import __main__
__main__.__requires__ = 'fedora_tagger'
import pkg_resources

from paste.deploy import loadapp
application = loadapp('config:/etc/fedoratagger/production.ini')
