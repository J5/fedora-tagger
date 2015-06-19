"""Cache icon url in the db for one bajillion speedups.

Revision ID: 410bc2e9d804
Revises: 3966341d4151
Create Date: 2015-06-19 15:56:38.722369

"""

# revision identifiers, used by Alembic.
revision = '410bc2e9d804'
down_revision = '3966341d4151'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('package', sa.Column(
        '_meta', sa.Unicode(length=255), server_default='{}', nullable=False))


def downgrade():
    op.drop_column('package', '_meta')
