# -*-coding:utf-8 -*-
import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))
print(os.path.abspath(os.path.join(__file__, "../..")))

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


def auto_renew_monthly_service(session):
    services = session.query(model.Service)\
        .filter(model.Service.type == model.Service.MONTHLY)\
        .filter(model.Service.auto_renew == True)\
        .filter(model.Service.alive == True).all()
    for service in services:
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
            shadowsocks_controller.add_port(service_password.port, service_password.password, False)

    if services is not None and len(services) > 0:
        shadowsocks_controller.restart_shadowsocks_listener()


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        auto_renew_monthly_service(session)
