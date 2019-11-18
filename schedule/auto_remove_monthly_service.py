# -*-coding:utf-8 -*-
"""
包月套餐自动失效脚本
每月执行，需要在『包月套餐自动续费脚本』之前执行
"""
from datetime import datetime

from util import shadowsocks_controller

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
    uri = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' \
          % (configs.DB_USER, configs.DB_PASSWORD, configs.DB_HOST, configs.DB_PORT, configs.DB_NAME)
    set_sqlalchemy_database_uri(uri)


def auto_remove_monthly_service(session):
    # TODO 如果Service过多，需要分片处理
    now = datetime.now()
    services = session.query(model.Service) \
        .filter(model.Service.type == model.Service.MONTHLY,
                model.Service.available.is_(True),
                model.Service.alive.is_(True),
                model.Service.reset_at < now).all()
    for service in services:  # type:model.Service
        service.available = False
        session.add(service)
        session.commit()

        service_password = session.query(model.ServicePassword) \
            .filter(model.ServicePassword.service_id == service.id).first()  # type:model.ServicePassword
        if service_password is not None:
            try:
                shadowsocks_controller.remove_port(service_password.port)
            except BaseException as e:
                print(e)
                continue


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        auto_remove_monthly_service(session)
