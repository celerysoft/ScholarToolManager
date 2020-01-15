#!/usr/bin/python3
# -*-coding:utf-8 -*-
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# ======================================== Legacy Database Start ======================================= #
import configs

legacy_uri = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' \
          % (configs.LEGACY_DB_USER, configs.LEGACY_DB_PASSWORD, configs.LEGACY_DB_HOST, configs.LEGACY_DB_PORT,
             configs.LEGACY_DB_NAME)
legacy_engine = create_engine(legacy_uri, pool_recycle=3600)
LegacySession = sessionmaker(bind=legacy_engine)
db = None
db_session = None


def set_db_with_pagination(db_inst):
    global db
    db = db_inst


def derive_db_session(pagination=False):
    if pagination:
        global db
        return db.session
    else:
        global db_session
        db_session = scoped_session(LegacySession)
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
def legacy_session_scope():
    global LegacySession
    session = LegacySession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# ========================================= Legacy Database End ======================================== #
uri = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' \
          % (configs.DB_USER, configs.DB_PASSWORD, configs.DB_HOST, configs.DB_PORT, configs.DB_NAME)
engine = create_engine(uri, pool_recycle=3600)
Session = sessionmaker(bind=engine)


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
