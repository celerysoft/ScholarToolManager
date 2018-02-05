# -*-coding:utf-8 -*-
from contextlib import contextmanager
from datetime import datetime

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


def transfer_service_to_new_service(session):
    services = session.query(model.OldService).all()

    for service in services:
        template = session.query(model.ServiceTemplate).filter(model.ServiceTemplate.id == service.template_id).first()

        create_at = datetime.fromtimestamp(service.created_at)
        expired_at = datetime.fromtimestamp(service.expired_at)
        if service.reset_at is not None:
            reset_at = datetime.fromtimestamp(service.reset_at)
        else:
            reset_at = None
        if service.last_reset_at is not None:
            last_reset_at = datetime.fromtimestamp(service.last_reset_at)
        else:
            last_reset_at = None
        new_service = model.Service(template_id=service.template_id, type=template.type, usage=service.usage,
                                    package=service.package, reset_at=reset_at, last_reset_at=last_reset_at,
                                    created_at=create_at, expired_at=expired_at,
                                    total_usage=service.total_usage, auto_renew=service.auto_renew,
                                    available=True, alive=True)

        session.add(new_service)
        session.commit()

        service_transfer_log = model.ServiceTransferLog(type=0, service_id=service.id,
                                                        new_service_id=new_service.id)
        session.add(service_transfer_log)
        session.commit()


def update_user_service(session):
    user_services = session.query(model.UserService).all()

    for user_service in user_services:
        old_service_id = user_service.service_id
        service_transfer_log = session.query(model.ServiceTransferLog) \
            .filter(model.ServiceTransferLog.service_id == old_service_id).first()
        user_service.service_id = service_transfer_log.new_service_id
        user_service.service_type = service_transfer_log.type


def update_service_password(session):
    service_passwords = session.query(model.ServicePassword).all()

    for service_password in service_passwords:
        old_service_id = service_password.service_id
        service_transfer_log = session.query(model.ServiceTransferLog) \
            .filter(model.ServiceTransferLog.service_id == old_service_id).first()
        service_password.service_id = service_transfer_log.new_service_id
        service_password.service_type = service_transfer_log.type


if __name__ == '__main__':
    init_database()

    with session_scope() as session:
        pass
        update_user_service(session)
        update_service_password(session)
        # transfer_service_to_new_service(session)
