'''
Mapping of tables needed in the sqlite database that goes to yum

This file was copied wholesale from pkgdb.
'''

from sqlalchemy import Table, Column, Integer, MetaData, Text

yummeta = MetaData()

YumTagsTable = Table(
    'packagetags',
    yummeta,
    Column('name', Text, nullable=False, primary_key=True),
    Column('tag', Text, nullable=False, primary_key=True),
    Column('score', Integer),
)
