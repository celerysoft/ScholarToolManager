# -*-coding:utf-8 -*-
import sys
import os
from datetime import datetime

from util import date_util

sys.path.append(os.path.abspath('..'))

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configs
import model

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


def auto_renew_monthly_service(session):
    services = session.query(model.Service).filter(model.Service.type == model.Service.MONTHLY).all()
    for service in services:
        service.reset_at = date_util.derive_1st_of_next_month()
        service.last_reset_at(datetime.now())


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        auto_renew_monthly_service(session)
