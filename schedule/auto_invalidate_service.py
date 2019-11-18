# -*-coding:utf-8 -*-
"""
套餐自动失效脚本
每天执行，需要在按月执行的脚本之后执行
"""
from datetime import datetime, timedelta

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


def auto_invalidate_data_service(session):
    # TODO 如果Service过多，需要分片处理
    now = datetime.now()
    # deadline为expired_at当月后两个月的结算日，比如在3月的结算日，只要让expired_at为2月1号之前的即可
    if now.month == 1:
        deadline = datetime(year=now.year - 1, month=12, day=1)
    else:
        deadline = datetime(year=now.year, month=now.month - 1, day=1)
    services = session.query(model.Service) \
        .filter(model.Service.type == model.Service.DATA,
                model.Service.expired_at < deadline,
                model.Service.available.is_(False),
                model.Service.alive.is_(True)).all()

    for service in services:  # type:model.Service
        service.alive = False
        session.add(service)
        session.commit()


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
        if now - service.reset_at > timedelta(days=2):
            service.alive = False
            session.add(service)
            session.commit()


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        auto_invalidate_data_service(session)
        auto_invalidate_monthly_service(session)
