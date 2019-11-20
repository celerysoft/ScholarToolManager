# -*-coding:utf-8 -*-
"""
包月套餐自动续费脚本
每月执行
"""
from datetime import datetime

from application.util import shadowsocks_controller
from application.util import date_util

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configs
from application.model import model

engine = None
Session = None


def set_sqlalchemy_database_uri(uri):
    global engine
    engine = create_engine(uri, pool_recycle=3600)
    global Session
    Session = sessionmaker(bind=engine)


@contextmanager
def _session_scope():
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


def auto_renew_monthly_service(session):
    services = session.query(model.Service) \
        .filter(model.Service.type == model.Service.MONTHLY,
                model.Service.auto_renew.is_(True),
                model.Service.alive.is_(True),
                model.Service.reset_at < datetime.now()).all()
    for service in services:  # type:model.Service
        # 扣费
        service_template = session.query(model.ServiceTemplate) \
            .filter(model.ServiceTemplate.id == service.template_id).first()
        if not service_template.available:
            print('该套餐已下架')
            continue

        user_scholar_balance = session.query(model.UserScholarBalance) \
            .filter(model.UserService.service_id == service.id) \
            .filter(model.User.id == model.UserService.user_id) \
            .filter(model.UserScholarBalance.user_id == model.User.id).first()

        if user_scholar_balance.balance >= service_template.price:
            user_scholar_balance.balance -= service_template.price

            user_scholar_balance_log = model.UserScholarBalanceLog(
                user_id=user_scholar_balance.user_id,
                amount=(-service_template.price),
                balance=user_scholar_balance.balance,
                message='包月套餐自动续费，套餐id: %s，套餐名称：%s' % (service.id, service_template.title)
            )
            session.add(user_scholar_balance_log)
        else:
            continue

        # 更新服务
        service.usage = 0
        service.reset_at = date_util.derive_1st_datetime_of_next_month()
        service.last_reset_at = datetime.now()
        service.available = True

        session.commit()

        service_password = session.query(model.ServicePassword) \
            .filter(model.ServicePassword.service_id == service.id).first()
        if service_password is not None:
            try:
                shadowsocks_controller.add_port(service_password.port, service_password.password)
            except BaseException as e:
                print(e)
                continue


if __name__ == '__main__':
    init_database()

    with _session_scope() as session:
        auto_renew_monthly_service(session)
