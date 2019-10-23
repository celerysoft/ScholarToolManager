# -*-coding:utf-8 -*-
"""
套餐自动失效脚本
每天执行
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
    # set_sqlalchemy_database_uri(configs.DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    set_sqlalchemy_database_uri(configs.ProductionConfig.SQLALCHEMY_DATABASE_URI)


def auto_invalidate_data_service(session):
    # TODO 如果Service过多，需要分片处理
    now = datetime.now()
    services = session.query(model.Service) \
        .filter(model.Service.type == model.Service.DATA,
                model.Service.expired_at < now,
                model.Service.available.is_(False),
                model.Service.alive.is_(True)).all()

    for service in services:  # type:model.Service
        if (now.year - service.expired_at.year) * 12 + now.month - service.expired_at.month > 12:
            service.available = False
            session.add(service)
            session.commit()

            service_password = session.query(model.ServicePassword) \
                .filter(model.ServicePassword.service_id == service.id).first()
            if service_password is not None:
                shadowsocks_controller.remove_port(service_password.port)


def auto_invalidate_monthly_service(session):
    # TODO 如果Service过多，需要分片处理
    now = datetime.now()
    services = session.query(model.Service) \
        .filter(model.Service.type == model.Service.MONTHLY,
                model.Service.alive.is_(True),
                model.Service.available.is_(False),
                model.Service.reset_at < now).all()
    for service in services:  # type:model.Service
        # 处于待续费的包月套餐在新开/上次续费的一年时间内，都可以继续续费，超过一年则无法续费
        if (now.year - service.last_reset_at.year) * 12 + now.month - service.last_reset_at.month > 12:
            service.available = False
            service.alive = False
            session.add(service)
            session.commit()

            service_password = session.query(model.ServicePassword) \
                .filter(model.ServicePassword.service_id == service.id).first()
            if service_password is not None:
                shadowsocks_controller.remove_port(service_password.port)


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        auto_invalidate_data_service(session)
        auto_invalidate_monthly_service(session)
