# -*-coding:utf-8 -*-
import sys
import os

sys.path.append(os.path.abspath('..'))

from datetime import datetime

from util import date_util, shadowsocks_controller

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
    # set_sqlalchemy_database_uri(configs.DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    set_sqlalchemy_database_uri(configs.ProductionConfig.SQLALCHEMY_DATABASE_URI)


def auto_remove_data_service(session):
    services = session.query(model.Service) \
        .filter(model.Service.type == model.Service.DATA) \
        .filter(model.Service.expired_at < datetime.now()) \
        .filter(model.Service.alive == True).all()

    for service in services:
        service.available = False
        service.alive = False
        session.add(service)
        session.commit()

        service_password = session.query(model.ServicePassword) \
            .filter(model.ServicePassword.service_id == service.id).first()
        if service_password is not None:
            shadowsocks_controller.remove_port(service_password.port, False)

    if services is not None and len(services) > 0:
        shadowsocks_controller.restart_shadowsocks_listener()


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        auto_remove_data_service(session)
