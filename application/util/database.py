#!/usr/bin/python3
# -*-coding:utf-8 -*-
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import configs

# ======================================== Legacy Database Start ======================================= #
legacy_uri = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' \
          % (configs.LEGACY_DB_USER, configs.LEGACY_DB_PASSWORD, configs.LEGACY_DB_HOST, configs.LEGACY_DB_PORT,
             configs.LEGACY_DB_NAME)
legacy_engine = create_engine(legacy_uri, pool_recycle=3600)
LegacySession = sessionmaker(bind=legacy_engine)

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
