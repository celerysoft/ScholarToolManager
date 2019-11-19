#!/usr/bin/python3
# -*-coding:utf-8 -*-
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = None
db = None
Session = None
db_session = None


def set_sqlalchemy_database_uri(uri):
    global engine
    engine = create_engine(uri, pool_recycle=3600)
    global Session
    Session = sessionmaker(bind=engine)


def set_db_with_pagination(db_inst):
    global db
    db = db_inst


def derive_db_session(pagination=False):
    if pagination:
        global db
        return db.session
    else:
        global db_session
        db_session = scoped_session(Session)
        return db_session
        # return scoped_session(Session)


def close_database():
    global db
    if db is not None and db.session is not None:
        db.session.remove()

    global db_session
    if db_session is not None:
        db_session.remove()


@contextmanager
def session_scope():
    global Session
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
