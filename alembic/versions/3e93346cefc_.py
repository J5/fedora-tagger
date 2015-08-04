""" Add a 'usage' table.

Revision ID: 3e93346cefc
Revises: None
Create Date: 2014-01-30 11:45:10.219678

"""

# revision identifiers, used by Alembic.
revision = '3e93346cefc'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('package_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'package_id')
    )


def downgrade():
    op.drop_table('usage')
