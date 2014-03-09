"""hash-ip

Revision ID: 3966341d4151
Revises: 3e93346cefc
Create Date: 2014-02-04 11:02:33.575568

"""

# revision identifiers, used by Alembic.
revision = '3966341d4151'
down_revision = '3e93346cefc'

from alembic import op
import sqlalchemy as sa

import fedoratagger as ft
import fedoratagger.lib.model as m
from fedoratagger.flask_utils import hsh


def upgrade():
    salt = ft.APP.config['SECRET_SALT']
    engine = op.get_bind().engine
    session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))
    users = session.query(m.FASUser).filter_by(anonymous=True).all()
    for user in users:
        try:
            user.username = hsh(user.username, salt)
            session.add(user)
            session.flush()
        except sa.exc.IntegrityError:
            # Then this user already has a hashed entry.  Just ignore them..
            session.rollback()

    session.commit()


def downgrade():
    # Not reversible
    pass
