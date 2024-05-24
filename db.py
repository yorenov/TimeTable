from peewee import *
import time
import json
from playhouse.migrate import *

conn = SqliteDatabase('database.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0}
                      )
migrator = SqliteMigrator(conn)


class BaseModel(Model):
    class Meta:
        database = conn


class Group(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name', unique=True)

    class Meta:
        table_name = 'groups'


class Lesson(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name', unique=True)

    class Meta:
        table_name = 'lessons'


class Teacher(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name', unique=True)

    class Meta:
        table_name = 'teachers'


class Audience(BaseModel):
    id = AutoField(column_name='id')
    name = TextField(column_name='name', unique=True)

    class Meta:
        table_name = 'audience'


class Subject(BaseModel):
    id = AutoField(column_name='id')

    group = TextField(column_name='group')
    year = IntegerField(column_name='year', default=0)
    week = IntegerField(column_name='week', default=0)
    day = IntegerField(column_name='day', default=0)

    subject_num = IntegerField(column_name='lesson_num', default=0)

    subject = TextField(column_name='subject', default='X')
    audience = TextField(column_name='audience', default='X')
    teacher = TextField(column_name='teacher', default='X')
    time = TextField(column_name='time', default='08:30 - 10:00')

    class Meta:
        table_name = 'subjects'


class AssociatedLesson(BaseModel):
    id = AutoField(column_name='id')

    subject = TextField(column_name='subject')
    teacher = TextField(column_name='teacher')

    class Meta:
        table_name = 'AssociatedLesson'


conn.connect()
Subject.create_table()
Group.create_table()
Teacher.create_table()
Audience.create_table()
Lesson.create_table()
AssociatedLesson.create_table()
cursor = conn.cursor()

conn.close()

