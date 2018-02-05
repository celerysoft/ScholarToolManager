# -*-coding:utf-8 -*-
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configs

engine = None
Session = None


def set_sqlalchemy_database_uri(uri):
    global engine
    engine = create_engine(uri, pool_recycle=3600)
    global Session
    Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    global Session
    session = Session()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def init_database():
    set_sqlalchemy_database_uri(configs.DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    # set_sqlalchemy_database_uri(configs.ProductionConfig.SQLALCHEMY_DATABASE_URI)


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        pass
