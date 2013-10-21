""" Since we added a new 'score' field, we should fill it with the old score.
"""

import os
os.environ['FEDORATAGGER_CONFIG'] = '/etc/fedoratagger/fedoratagger.cfg'

import fedoratagger

ses = fedoratagger.SESSION

import fedoratagger.lib.model as m

users = ses.query(m.FASUser).all()

for user in users:
    if user.score == 0:
        user.score = len(user.votes)

ses.commit()
