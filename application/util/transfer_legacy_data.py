# -*-coding:utf-8 -*-
"""
Transfer v1.0 data format to v2.0 data format
"""
from datetime import datetime

import configs
from application.model.event import Event
from application.model.legacy import model
from application.model.role import Role
from application.model.scholar_payment_account import ScholarPaymentAccount
from application.model.service import Service
from application.model.service_template import ServiceTemplate
from application.model.user import User
from application.model.user_role import UserRole
from application.util.database import session_scope, legacy_session_scope


class TransferLegacyDataToolkit(object):
    def execute(self) -> bool:
        with legacy_session_scope() as legacy_session, session_scope() as session:
            try:
                self._create_built_in_role(session)
                self._transfer_user_and_scholar_payment_account(legacy_session, session)
                self._transfer_event(legacy_session, session)
                self._transfer_service_template(legacy_session, session)
                self._transfer_service(legacy_session, session)

                session.commit()
            except BaseException as e:
                if configs.DEBUG:
                    raise RuntimeError(e)
                return False
            return True

    @classmethod
    def _create_built_in_role(cls, session):
        for built_in_permission_enum in Role.BuiltInRole:
            built_in_role = built_in_permission_enum.value  # type: Role.BuiltInRole.BuiltInRoleObject
            role = Role(
                name=built_in_role.name,
                description=built_in_role.description,
            )
            session.add(role)
        # session.commit()
        session.flush()

    @classmethod
    def _transfer_user_and_scholar_payment_account(cls, legacy_session, session):
        legacy_users = legacy_session.query(model.User).filter(model.User.available.is_(True)).all()
        for legacy_user in legacy_users:  # type: model.User
            user = User(
                username=legacy_user.username,
                email=legacy_user.email,
                password=legacy_user.password,
            )
            user.created_at = datetime.fromtimestamp(legacy_user.created_at)
            user.status = User.STATUS.ACTIVATED
            session.add(user)
            session.flush()

            cls._transfer_scholar_payment_account_for_user(legacy_session, session, user.uuid, legacy_user.id)
            cls._assign_role_for_user(session, user.uuid, Role.BuiltInRole.REGISTRATION_USER)

    @staticmethod
    def _transfer_scholar_payment_account_for_user(legacy_session, session, user_uuid: str, legacy_user_id: int):
        legacy_user_balance = legacy_session.query(model.UserScholarBalance).filter(
            model.UserScholarBalance.user_id == legacy_user_id).first()  # type: model.UserScholarBalance

        scholar_payment_account = ScholarPaymentAccount(
            user_uuid=user_uuid,
            balance=legacy_user_balance.balance,
        )
        session.add(scholar_payment_account)

    @staticmethod
    def _assign_role_for_user(session, user_uuid, role: Role.BuiltInRole):
        role = session.query(Role).filter(Role.name == role.value.name).first()  # type: Role
        user_role = UserRole(
            user_uuid=user_uuid,
            role_uuid=role.uuid,
        )
        session.add(user_role)

    @staticmethod
    def _transfer_event(legacy_session, session):
        legacy_events = legacy_session.query(model.Event).all()
        for legacy_event in legacy_events:  # type: model.Event
            legacy_user = legacy_session.query(model.User).filter(model.User.id == legacy_event.user_id).first()
            user = session.query(User).filter(User.username == legacy_user.username).first()
            event = Event(
                author_uuid=user.uuid,
                title=legacy_event.name,
                summary=legacy_event.summary,
                content=legacy_event.content,
            )
            event.created_at = datetime.fromtimestamp(legacy_event.created_at)
            event.status = Event.Status.VALID.value if legacy_event.available else Event.Status.DELETED.value
            session.add(event)


    @staticmethod
    def _transfer_service_template(legacy_session, session):
        legacy_templates = legacy_session.query(model.ServiceTemplate).all()
        for legacy_template in legacy_templates:  # type: model.ServiceTemplate
            template = ServiceTemplate(
                service_type=legacy_template.type,
                title=legacy_template.title,
                subtitle=legacy_template.subtitle,
                description=legacy_template.description,
                package=legacy_template.balance,
                price=legacy_template.price,
                initialization_fee=legacy_template.initialization_fee,
                status=0
            )
            if legacy_template.available:
                template.status = ServiceTemplate.STATUS.VALID
            else:
                template.status = ServiceTemplate.STATUS.SUSPEND
            session.add(template)

    @staticmethod
    def _transfer_service(legacy_session, session):
        pass
        legacy_services = legacy_session.query(model.Service).filter(model.Service.alive.is_(True)).all()
        for legacy_service in legacy_services:  # type: model.Service
            legacy_user_service = legacy_session.query(model.UserService).filter(
                model.UserService.service_id == legacy_service.id).first()  # type: model.UserService
            legacy_user = legacy_session.query(model.User).filter(
                model.User.id == legacy_user_service.user_id).first()   # type: model.User
            legacy_service_password = legacy_session.query(model.ServicePassword).filter(
                model.ServicePassword.service_id == legacy_service.id).first()  # type: model.ServicePassword
            user = session.query(User).filter(
                User.username == legacy_user.username).first()  # type: User
            legacy_service_template = legacy_session.query(model.ServiceTemplate).filter(
                model.ServiceTemplate.id == legacy_service.template_id).first()  # type: model.ServiceTemplate
            service_template = session.query(ServiceTemplate).filter(
                ServiceTemplate.type == legacy_service_template.type,
                ServiceTemplate.package == legacy_service_template.balance).first()  # type: ServiceTemplate

            if legacy_service.type == model.Service.MONTHLY:
                billing_date = legacy_service.last_reset_at
            else:
                billing_date = legacy_service.expired_at
            service = Service(
                user_uuid=user.uuid,
                template_uuid=service_template.uuid,
                service_type=legacy_service.type,
                package=legacy_service_template.balance,
                usage=legacy_service.usage,
                auto_renew=1 if legacy_service.auto_renew else 0,
                billing_date=billing_date,
                total_usage=legacy_service.total_usage,
                port=legacy_service_password.port,
                password=legacy_service_password.password,
            )
            if service.usage > service.package:
                service.status = Service.STATUS.OUT_OF_CREDIT
            else:
                service.status = Service.STATUS.ACTIVATED
            session.add(service)


toolkit = TransferLegacyDataToolkit()
