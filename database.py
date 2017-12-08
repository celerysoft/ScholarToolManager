#!/usr/bin/python3
# -*-coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = None
db_session = None
db = None


def set_sqlalchemy_database_uri(uri):
    global engine
    engine = create_engine(uri)
    global db_session
    db_session = scoped_session(sessionmaker(bind=engine))


def set_db_with_pagination(db_inst):
    global db
    db = db_inst


def derive_db_session(pagination=False):
    if pagination:
        global db
        return db.session
    else:
        global db_session
        return db_session


def close_database():
    if db is not None and db.session is not None:
        db.session.remove()

    if db_session is not None:
        db_session.remove()
